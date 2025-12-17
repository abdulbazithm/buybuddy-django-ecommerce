from django.utils.text import slugify
from store.models import Category, Brand, Product


def seed_data():
    # 🛑 If products already exist, do nothing
    if Product.objects.exists():
        return

    # =====================
    # Categories
    # =====================
    categories = [
        {
            "name": "Electronics",
            "description": "Electronic gadgets and devices"
        },
        {
            "name": "Fashion",
            "description": "Clothing and fashion accessories"
        },
        {
            "name": "Groceries",
            "description": "Daily grocery essentials"
        },
    ]

    category_objs = {}
    for cat in categories:
        obj, _ = Category.objects.get_or_create(
            name=cat["name"],
            defaults={
                "slug": slugify(cat["name"]),
                "description": cat["description"],
                "is_active": True,
            }
        )
        category_objs[cat["name"]] = obj

    # =====================
    # Brands
    # =====================
    brands = ["Samsung", "Nike", "Local Farm"]

    brand_objs = {}
    for brand in brands:
        obj, _ = Brand.objects.get_or_create(
            name=brand,
            defaults={
                "description": f"{brand} brand products",
                "is_active": True,
            }
        )
        brand_objs[brand] = obj

    # =====================
    # Products
    # =====================
    products = [
        {
            "name": "Samsung Galaxy Smartphone",
            "category": "Electronics",
            "brand": "Samsung",
            "price": 14999,
            "stock": 10,
            "description": "Latest Samsung smartphone with modern features",
        },
        {
            "name": "Men Cotton T-Shirt",
            "category": "Fashion",
            "brand": "Nike",
            "price": 599,
            "stock": 25,
            "description": "Comfortable cotton t-shirt for daily wear",
        },
        {
            "name": "Organic Rice 5kg",
            "category": "Groceries",
            "brand": "Local Farm",
            "price": 499,
            "stock": 50,
            "description": "Healthy organic rice for family use",
        },
    ]

    for product in products:
        Product.objects.create(
            name=product["name"],
            slug=slugify(product["name"]),
            category=category_objs[product["category"]],
            brand=brand_objs[product["brand"]],
            price=product["price"],
            stock=product["stock"],
            description=product["description"],
            is_available=True,
        )
