from django.utils.text import slugify
from store.models import Category, Brand, Product, ProductImage
from django.core.files import File
import os
from buybuddy.settings import BASE_DIR

def seed_data():

    # =====================
    # Categories
    # =====================
    category_list = [
        "Electronics",
        "Fashion",
        "Home & Kitchen",
        "Beauty",
        "Grocery",
        "Books"
    ]

    category_objs = {}
    for name in category_list:
        obj, _ = Category.objects.get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "description": f"Demo products for {name}",
                "is_active": True,
            }
        )
        category_objs[name] = obj

    # =====================
    # Brand
    # =====================
    brand_obj, _ = Brand.objects.get_or_create(
        name="Demo Brand",
        defaults={"description": "Demo Brand products", "is_active": True}
    )

    # =====================
    # Products + Images
    # =====================
    products = [
        {"name": "Smartphone", "category": "Electronics", "image": "electronics.jpg", "price": 14999},
        {"name": "Men T-Shirt", "category": "Fashion", "image": "fashion.jpg", "price": 599},
        {"name": "Blender", "category": "Home & Kitchen", "image": "home_kitchen.jpg", "price": 2499},
        {"name": "Lipstick", "category": "Beauty", "image": "beauty.jpg", "price": 399},
        {"name": "Organic Rice 5kg", "category": "Grocery", "image": "grocery.jpg", "price": 499},
        {"name": "As Long As the Lemon Trees Grow", "category": "Books", "image": "books.jpg", "price": 799},
    ]

    for prod in products:
        # Create product if it does not exist
        product_obj, created = Product.objects.get_or_create(
            name=prod["name"],
            defaults={
                "slug": slugify(prod["name"]),
                "category": category_objs[prod["category"]],
                "brand": brand_obj,
                "price": prod["price"],
                "stock": 10,
                "description": f"Demo product: {prod['name']}",
                "is_available": True,
            }
        )

        # Add product image if not already exists
        if not ProductImage.objects.filter(product=product_obj).exists():
            image_path = os.path.join(BASE_DIR, "store/static/store/images", prod["image"])
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    ProductImage.objects.create(
                        product=product_obj,
                        image=File(f),
                        is_featured=True
                    )
