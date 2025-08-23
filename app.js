// DOM Elements
const userDropdownToggle = document.getElementById('userDropdownToggle');
const userDropdown = document.getElementById('userDropdown');
const userText = document.getElementById('userText');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const logoutBtn = document.getElementById('logoutBtn');
const cartItems = document.getElementById('cart-items');
const emptyCartMessage = document.getElementById('empty-cart-message');
const cartSubtotal = document.getElementById('cart-subtotal');
const cartTax = document.getElementById('cart-tax');
const cartTotal = document.getElementById('cart-total');
const checkoutBtn = document.getElementById('checkout-btn');
const cartCount = document.getElementById('cart-count');

// User state
let currentUser = null;
let cart = [];

/* -----USER DROPDOWN HANDLING------- */
userDropdownToggle.addEventListener('click', e => {
  e.preventDefault();
  userDropdown.classList.toggle('show');
});

document.addEventListener('click', e => {
  if (!userDropdownToggle.contains(e.target) && !userDropdown.contains(e.target)) {
    userDropdown.classList.remove('show');
  }
});

/* -----AUTH (Still functional if needed)-------- */
loginForm.addEventListener('submit', function (e) {
  e.preventDefault();
  const email = this.querySelector('input[type="email"]').value;
  const password = this.querySelector('input[type="password"]').value;

  if (email && password) {
    currentUser = { email, name: email.split('@')[0] };
    updateUserUI();
    bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
  }
});

registerForm.addEventListener('submit', function (e) {
  e.preventDefault();
  const name = this.querySelector('input[type="text"]').value;
  const email = this.querySelector('input[type="email"]').value;
  const password = this.querySelector('input[type="password"]').value;

  if (name && email && password) {
    currentUser = { email, name };
    updateUserUI();
    new bootstrap.Tab(document.getElementById('login-tab')).show();
    bootstrap.Modal.getInstance(document.getElementById('authModal')).hide();
  }
});

logoutBtn.addEventListener('click', e => {
  e.preventDefault();
  currentUser = null;
  updateUserUI();
});

function toggleMenu() {
    document.getElementById("navLinks").classList.toggle("active");
  } 
  
function updateUserUI() {
  if (currentUser) {
    userText.textContent = currentUser.name;
    logoutBtn.classList.remove('d-none');
  } else {
    userText.textContent = 'Login';
    logoutBtn.classList.add('d-none');
  }
  userDropdown.classList.remove('show');
}


// Add to cart 
function addToCart(productName, productPrice) {
  const existingItem = cart.find(item => item.name === productName);

  if (existingItem) {
    existingItem.quantity++;
  } else {
    cart.push({ name: productName, price: productPrice, quantity: 1 });
  }

  updateCartUI();

  // Scroll to top after adding
  window.scrollTo({ top: 0, behavior: "smooth" });
}
// Remove from cart
function removeFromCart(productName) {
  cart = cart.filter(item => item.name !== productName);
  updateCartUI();
}

// Update cart UI
function updateCartUI() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  cartCount.textContent = totalItems;

  if (cart.length === 0) {
    emptyCartMessage.classList.remove('d-none');
    cartItems.innerHTML = '';
    checkoutBtn.disabled = true;
    cartSubtotal.textContent = "₹0.00";
    cartTax.textContent = "₹0.00";
    cartTotal.textContent = "₹0.00";
    return;
  }

  emptyCartMessage.classList.add('d-none');
  checkoutBtn.disabled = false;

  let itemsHTML = '';
  let subtotal = 0;

  cart.forEach(item => {
    const itemTotal = item.price * item.quantity;
    subtotal += itemTotal;

    itemsHTML += `
      <div class="cart-item d-flex justify-content-between align-items-center mb-3">
        <div>
          <h6 class="mb-0">${item.name}</h6>
          <small class="text-muted">₹${item.price} x ${item.quantity}</small>
        </div>
        <div>
          <span class="fw-bold">₹${itemTotal}</span>
          <button class="btn btn-sm btn-outline-danger ms-2" onclick="removeFromCart('${item.name}')">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    `;
  });

  cartItems.innerHTML = itemsHTML;

  const tax = subtotal * 0.18; // 18% tax
  const shipping = 40;
  const total = subtotal + tax + shipping;

  cartSubtotal.textContent = `₹${subtotal.toFixed(2)}`;
  cartTax.textContent = `₹${tax.toFixed(2)}`;
  cartTotal.textContent = `₹${total.toFixed(2)}`;
}

//PAGE SWITCH

function showPage(pageId) {
  document.querySelectorAll('.page-section').forEach(page => page.classList.remove('active'));
  document.getElementById(`${pageId}-page`).classList.add('active');
  window.scrollTo(0, 0);
}

//INIT
document.addEventListener('DOMContentLoaded', updateCartUI);



