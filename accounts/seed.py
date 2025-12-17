from django.utils.text import slugify
from store.models import Category, Brand, Product, ProductImage
from django.core.files import File
import os
from buybuddy.settings import BASE_DIR

def seed_data():
    # 🛑 If products already exist, do nothing
    if Product.objects.exists():
        return

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
    # Brands (optional demo)
    # =====================
    brand_names = ["Demo Brand"]
    brand_objs = {}
    for brand in brand_names:
        obj, _ = Brand.objects.get_or_create(
            name=brand,
            defaults={"description": f"{brand} products", "is_active": True}
        )
        brand_objs[brand] = obj

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
        product_obj = Product.objects.create(
            name=prod["name"],
            slug=slugify(prod["name"]),
            category=category_objs[prod["category"]],
            brand=brand_objs["Demo Brand"],
            price=prod["price"],
            stock=10,
            description=f"Demo product: {prod['name']}",
            is_available=True,
        )

        # Add product image
        image_path = os.path.join(BASE_DIR, "store/static/store/images", prod["image"])
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                ProductImage.objects.create(
                    product=product_obj,
                    image=File(f),
                    is_featured=True
                )
