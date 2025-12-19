from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>/", views.productView, name="ProductView"),
    path("checkout/",views.checkout, name="Checkout"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy-now"),
     path("payment_success/", views.payment_success, name="payment_success"), 
    path("payment_cancel/", views.payment_failed, name="payment_failed"),
    path('category/<str:category_name>/', views.category_products, name='category_products'),
    path("cart/", views.cart_view, name="cart"),
    path("cart-count/", views.cart_count, name="cart_count"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add-to-cart"),
    path("remove-from-cart/<int:product_id>/", views.remove_from_cart, name="RemoveFromCart"),
    path("increase/<int:product_id>/", views.increase_quantity, name="IncreaseQty"),
    path("decrease/<int:product_id>/", views.decrease_quantity, name="DecreaseQty"),
<<<<<<< HEAD
]  
>>>>>>> 727ff3c455944ac64a3e4bbb9d1016c49d27da25
