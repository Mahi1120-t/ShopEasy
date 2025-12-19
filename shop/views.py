from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, TeamMember, Order, OrderUpdate
from django.http import JsonResponse
from math import ceil
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
from decimal import Decimal, ROUND_HALF_UP
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

# ----------------- Home Page -----------------
def index(request):
    products = Product.objects.all()
    cart_session = request.session.get('cart', {})

    cart_items = {}
    for product_id, qty in cart_session.items():
        if isinstance(qty, dict):
            qty = qty.get("quantity", 0)
        product = get_object_or_404(Product, id=int(product_id))
        cart_items[product_id] = {
            "product": product,
            "quantity": qty
        }

    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}

    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides+1), nSlides])

    return render(request, "shop/index.html", {'allProds': allProds, 'cart_items': cart_items})


# ----------------- Static Pages -----------------
def about(request):
    members = TeamMember.objects.all()
    return render(request, 'shop/about.html', {'team_members': members})

def contact(request):
    return render(request, "shop/contact.html")


@csrf_exempt
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get("orderId", "").strip()
        email = request.POST.get("email", "").strip().lower()
        
        try:
            order = Order.objects.get(id=orderId, email__iexact=email)
            updates = OrderUpdate.objects.filter(order=order).order_by('timestamp')
            
            updates_list = []
            for u in updates:
                updates_list.append({
                    "text": u.update_desc, 
                    "time": u.timestamp.strftime("%d-%m-%Y %H:%M:%S")
                })
            
            return JsonResponse({
                "status": "success", 
                "updates": updates_list, 
                "items_json": order.items_json
            })
            
        except Order.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "No order found with these details. Please check your Order ID and Email."
            })
        except Exception as e:
            return JsonResponse({
                "status": "error", 
                "message": f"An error occurred: {str(e)}"
            })
    
    return render(request, "shop/tracker.html")


def search(request):
    query = request.GET.get("q", "")
    results = Product.objects.filter(Q(product_name__icontains=query) | Q(desc__icontains=query)) if query else []
    return render(request, "shop/search.html", {"query": query, "results": results})


def productView(request, myid):
    product = get_object_or_404(Product, id=myid)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'shop/prodView.html', {'product': product, 'similar_products': similar_products})


# ----------------- Cart -----------------
def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(qty.get("quantity", qty) if isinstance(qty, dict) else qty for qty in cart.values())
    return JsonResponse({'count': count})


def get_cart_details(request):
    cart = request.session.get("cart", {})
    cart_items = []
    subtotal = Decimal("0.00")

    for product_id, qty in cart.items():
        quantity = qty.get("quantity", qty) if isinstance(qty, dict) else qty
        try:
            product = Product.objects.get(id=product_id)
            price = Decimal(str(product.price))  # convert float to Decimal
            total_price = price * Decimal(quantity)
            subtotal += total_price
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "total_price": total_price
            })
        except Product.DoesNotExist:
            continue

    tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = subtotal + tax

    return cart_items, subtotal, tax, total


def cart_view(request):
    cart_items, subtotal, tax, total = get_cart_details(request)
    shipping = Decimal("0.00") if subtotal >= 1000 else Decimal("100.00")
    grand_total = total + shipping

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": subtotal,
        "gst": tax,
        "shipping": "Free Shipping" if shipping==0 else f"₹{shipping}",
        "final_total": grand_total
    })


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        if isinstance(cart[product_id], dict):
            cart[product_id]["quantity"] += 1
        else:
            cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


def increase_quantity(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        if isinstance(cart[product_id], dict):
            cart[product_id]["quantity"] += 1
        else:
            cart[product_id] += 1
        request.session.modified = True
    return redirect("cart")


def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        if isinstance(cart[product_id], dict):
            cart[product_id]["quantity"] -= 1
            qty = cart[product_id]["quantity"]
        else:
            cart[product_id] -= 1
            qty = cart[product_id]
        if qty <= 0:
            del cart[product_id]
        request.session.modified = True
    return redirect("cart")


# ----------------- Checkout -----------------

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    cart_items, subtotal, tax, total = get_cart_details(request)
    shipping = Decimal("0.00") if subtotal >= 1000 else Decimal("100.00")
    final_total = total + shipping

    # Save order in DB
    items_json = {str(item["product"].id): [item["product"].product_name, item["quantity"], str(item["product"].price)] for item in cart_items}
    order = Order.objects.create(
        items_json=json.dumps(items_json),
        name=request.user.username if request.user.is_authenticated else "Guest",
        email=request.user.email if request.user.is_authenticated else "guest@example.com",
        address="Test Address",
        city="Test City",
        state="Test State",
        zip_code="000000",
        phone="0000000000",
        amount=float(final_total)
    )
    OrderUpdate.objects.create(order=order, update_desc="Order placed successfully")

    # Stripe line items
    line_items = []
    for item in cart_items:
        price = int(Decimal(str(item["product"].price)) * 100)
        line_items.append({
            "price_data": {
                "currency": "inr", 
                "product_data": {"name": item["product"].product_name}, 
                "unit_amount": price
            },
            "quantity": item["quantity"]
        })
    if shipping > 0:
        line_items.append({
            "price_data": {
                "currency": "inr", 
                "product_data": {"name": "Shipping"}, 
                "unit_amount": int(shipping*100)
            },
            "quantity": 1
        })

    # Use request.build_absolute_uri for dynamic URLs
    success_url = request.build_absolute_uri('/shop/payment_success/') + f'?order_id={order.id}'
    cancel_url = request.build_absolute_uri('/shop/payment_cancel/')

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url
    )

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "total": final_total,
        "session_id": session.id,
        "public_key": settings.STRIPE_PUBLISHABLE_KEY,
        "orderId": order.id
    })

def payment_success(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        messages.error(request, "Order ID missing.")
        return redirect('ShopHome')

    try:
        order = Order.objects.get(id=order_id)
        customer_email = order.email  # This should be the customer's email
        
        print(f"Sending email to: {customer_email}")  # Debug line
        
        # Send confirmation email to CUSTOMER
        subject = f'Order Confirmation - Order #{order.id} - Shopzy'
        message = f"""
Dear {order.name},

Thank you for your order! Your payment was successful and your order has been confirmed.

Order Details:
- Order ID: {order.id}
- Amount: ₹{order.amount}
- Shipping Address: {order.address}, {order.city}, {order.state} - {order.zip_code}
- Phone: {order.phone}

We will notify you when your order ships. You can track your order status anytime using your Order ID and email.

Thank you for shopping with us!

Best regards,
Shopzy Team
        """
        
        # Send email to CUSTOMER
        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,  # From address (your shop email)
            [customer_email],  # TO: Customer's email address
            fail_silently=False,
        )
        
        print(f"Email sent successfully to {customer_email}")  # Debug line
        
        # Clear cart session after success
        if 'cart' in request.session:
            del request.session['cart']
            
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('ShopHome')
    except Exception as e:
        print(f"Email sending failed: {e}")  # Debug line

    return render(request, 'shop/success.html', {'order': order})

def payment_failed(request):
    return render(request, "shop/failed.html")


def buy_now(request, product_id):
    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart
    return redirect("Checkout")


def category_products(request, category_name):
    products = Product.objects.filter(category__iexact=category_name)

    # --- Filters ---
    prices = request.GET.getlist("price")      
    discounts = request.GET.getlist("discount")
    ratings = request.GET.getlist("rating")    
    color = request.GET.get("color")           

    # ---- Price Filter ----
    if prices:
        price_q = Q()
        for p in prices:
            if p == "0-1000":
                price_q |= Q(price__gte=Decimal("0.00"), price__lte=Decimal("1000.00"))
            elif p == "1000-2000":
                price_q |= Q(price__gte=Decimal("1000.00"), price__lte=Decimal("2000.00"))
            elif p == "2000-5000":
                price_q |= Q(price__gte=Decimal("2000.00"), price__lte=Decimal("5000.00"))
            elif p == "5000+":
                price_q |= Q(price__gte=Decimal("5000.00"))
        products = products.filter(price_q)

    # ---- Discount Filter ----
    if discounts:
        discount_q = Q()
        for d in discounts:
            try:
                discount_q |= Q(discount__gte=int(d))
            except ValueError:
                continue
        products = products.filter(discount_q)

    # ---- Rating Filter ----
    if ratings:
        rating_q = Q()
        for r in ratings:
            try:
                rating_q |= Q(rating__gte=float(r))
            except ValueError:
                continue
        products = products.filter(rating_q)

    # ---- Color Filter ----
    if color:
        products = products.filter(color__iexact=color)

    # --- Prepare context ---
    context = {
        'products': products,
        'category': category_name,
        'selected_prices': prices,
        'selected_discounts': discounts,
        'selected_ratings': ratings,
        'selected_color': color,
    }

    return render(request, 'shop/category_products.html', context)
