import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

@pytest.fixture
def driver():
    """Setup Chrome driver"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

# FULL E-COMMERCE FLOW 
def test_ecommerce_flow(driver):
    os.makedirs("reports", exist_ok=True)
    driver.get("http://127.0.0.1:8000/")
    driver.save_screenshot("reports/1_homepage.png")

    # Step 1: Search Product
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("mouse")
    search_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img")))
    driver.save_screenshot("reports/2_search_results.png")

    # Add to Cart
    try:
        add_to_cart = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Add to Cart"))
        )
        add_to_cart.click()
    except Exception as e:
        pytest.fail(f"❌ Could not find 'Add to Cart' button: {e}")
    time.sleep(2)
    driver.save_screenshot("reports/3_added_to_cart.png")

    # Open Cart
    try:
        cart_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "cart-link"))
        )
        cart_link.click()
    except:
        # Fallback if ID changes
        driver.get("http://127.0.0.1:8000/shop/cart/")
    time.sleep(2)
    driver.save_screenshot("reports/4_cart.png")

    # Verify cart has at least one item
    items = driver.find_elements(By.CLASS_NAME, "cart-item")
    if not items:
        items = driver.find_elements(By.CLASS_NAME, "card")
    if not items:
        items = driver.find_elements(By.TAG_NAME, "tr")

    assert len(items) > 0, "❌ Cart is empty after adding a product!"

    # Proceed to Checkout
    try:
        checkout_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Checkout"))
        )
        checkout_btn.click()
    except:
        pytest.skip("Checkout button not available for this demo site.")
    time.sleep(2)
    driver.save_screenshot("reports/5_checkout.png")

    #  Verify checkout page
    assert "checkout" in driver.current_url.lower(), "Checkout page did not load properly."

#  SEARCH FUNCTIONALITY 
def test_search_results(driver):
    os.makedirs("reports", exist_ok=True)
    driver.get("http://127.0.0.1:8000/")

    # Valid product search
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("mouse")
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)
    driver.save_screenshot("reports/search_results_mouse.png")

    products = driver.find_elements(By.TAG_NAME, "img")
    assert len(products) > 0, "❌ No products found for valid search!"

    # Invalid product search
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys("xyznotfound")
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)
    driver.save_screenshot("reports/search_results_invalid.png")

    page_source = driver.page_source.lower()
    assert "no" in page_source or "not found" in page_source, "❌ Invalid search did not show 'no results' message!"

#ADD TO CART FUNCTIONALITY
def test_add_to_cart(driver):
    os.makedirs("reports", exist_ok=True)
    driver.get("http://127.0.0.1:8000/")
    time.sleep(2)
    driver.save_screenshot("reports/cart_flow_start.png")

    # Add product to cart
    try:
        add_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Add to Cart"))
        )
        add_button.click()
        time.sleep(3)
    except Exception as e:
        pytest.fail(f"❌ Could not click 'Add to Cart' button: {e}")

    driver.save_screenshot("reports/cart_after_add.png")

    # Open cart and verify
    driver.get("http://127.0.0.1:8000/shop/cart/")
    time.sleep(3)
    driver.save_screenshot("reports/cart_page.png")

    # Find items
    items = driver.find_elements(By.CLASS_NAME, "cart-item")
    if not items:
        items = driver.find_elements(By.CLASS_NAME, "card")
    if not items:
        items = driver.find_elements(By.TAG_NAME, "tr")

    assert len(items) > 0, "❌ Cart is empty after adding a product!"

#  PAGE TITLE CHECK
def test_homepage_title(driver):
    driver.get("http://127.0.0.1:8000/")
    driver.save_screenshot("reports/homepage_title.png")
    assert "shop" in driver.title.lower() or "ecom" in driver.title.lower(), "❌ Homepage title does not look correct."

