import os
import django
from collections import defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecom.settings')
django.setup()

from shop.models import Product

# Define categories and keywords
categories = {
    'groceries': ['rice', 'wheat', 'milk', 'oil'],
    'mobiles': ['phone', 'mobile', 'samsung', 'iphone'],
    'fashion': ['shirt', 'jeans', 'dress', 't-shirt'],
    'electronics': ['laptop', 'tv', 'camera', 'headphone'],
    'appliances': ['blender', 'mixer', 'oven', 'refrigerator'],
    'beauty': ['lipstick', 'perfume', 'cream', 'shampoo'],
    'toys & more': ['toy', 'puzzle', 'game', 'lego']
}

# Dictionary to keep count
category_count = defaultdict(int)

# Assign categories
for product in Product.objects.all():
    assigned = False
    name_lower = product.product_name.lower()
    for cat, keywords in categories.items():
        if any(keyword.lower() in name_lower for keyword in keywords):
            product.category = cat
            product.save()
            category_count[cat] += 1
            assigned = True
            break
    if not assigned:
        product.category = 'others'
        product.save()
        category_count['others'] += 1

# Print summary
print("Category assignment complete!\nSummary:")
for cat, count in category_count.items():
    print(f"{cat}: {count} products")
