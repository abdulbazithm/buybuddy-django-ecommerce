from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from store.models import Product
from .models import Wishlist

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect(request.META.get('HTTP_REFERER', 'store'))

@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect('my_wishlist')

@login_required
def my_wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/my_wishlist.html', {'items': items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item = Wishlist.objects.filter(user=request.user, product=product)

    if item.exists():
        item.delete()  # remove
    else:
        Wishlist.objects.create(user=request.user, product=product)  # add

    return redirect(request.META.get('HTTP_REFERER', 'store'))
