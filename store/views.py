from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Brand, ProductImage, Review
from orders.models import OrderItem
from wishlist.models import Wishlist
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages

# 🏠 Home Page
def home(request):
    products = Product.objects.filter(is_available=True).prefetch_related('images')
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    # ⭐ Add Wishlist IDs for logged-in users
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'brands': brands,
        'wishlist_ids': wishlist_ids,
    })



# 📦 Product Detail Page
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    images = ProductImage.objects.filter(product=product)

    # wishlist checking already here
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    # Fetch reviews
    reviews = product.reviews.all()

    # Check if user can review
    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            order__status="Delivered",
            product=product
        ).exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'can_review': can_review,
    })


def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)

    return render(request, "store/category_products.html", {
        "category": category,
        "products": products,
    })

def search_products(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category")
    brand = request.GET.get("brand")
    price = request.GET.get("price")
    sort = request.GET.get("sort")

    products = Product.objects.filter(is_available=True)

    # 🔍 TEXT SEARCH
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # 🏷 CATEGORY FILTER
    if category:
        products = products.filter(category_id=category)

    # 🏭 BRAND FILTER
    if brand:
        products = products.filter(brand_id=brand)

    # 💰 PRICE FILTER
    if price:
        min_price, max_price = price.split("-")
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # ↕ SORTING
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")
    elif sort == "new":
        products = products.order_by("-id")

    # Load categories & brands for dropdown
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)

    return render(request, "store/search_results.html", {
        "query": query,
        "products": products,
        "categories": categories,
        "brands": brands,
    })




@login_required
def add_review(request, order_item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=order_item_id,
        order__user=request.user,
        order__status="DELIVERED"
    )

    # Check if review already exists (Amazon-style rule)
    if hasattr(order_item, 'review'):
        messages.error(request, "You have already reviewed this item.")
        return redirect('order_detail', order_item.order.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.order_item = order_item
            r.product = order_item.product
            r.user = request.user
            r.save()

            messages.success(request, "Review submitted!")
            return redirect('product_detail', slug=order_item.product.slug)
    else:
        form = ReviewForm()

    return render(request, 'store/add_review.html', {
        'form': form,
        'product': order_item.product
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully.")
            return redirect('product_detail', slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'store/edit_review.html', {
        'form': form,
        'review': review,
        'product': review.product
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        product_slug = review.product.slug
        review.delete()
        messages.success(request, "Review deleted successfully.")
        return redirect('product_detail', slug=product_slug)

    return render(request, 'store/delete_review.html', {
        'review': review,
        'product': review.product
    })
