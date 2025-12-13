from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product
from django.contrib.auth.decorators import login_required

# Add product to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created_item = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created_item:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('home')


# View Cart
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = cart.get_total()
    return render(request, 'cart/view_cart.html', {'cart': cart, 'items': items, 'total': total})


# Remove item from cart
@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('view_cart')


# Update quantity
@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    return redirect('view_cart')

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = cart.get_total()
    addresses = Address.objects.filter(user=request.user)

    if request.method == "POST":
        address_id = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        if not items:
            messages.error(request, "Your cart is empty!")
            return redirect("view_cart")

        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect("checkout")

        address = Address.objects.get(id=address_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
            payment_method=payment_method,
            status="Processing"
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        items.delete()

        tracking_no = "BB" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        Shipment.objects.create(order=order, tracking_no=tracking_no)

        return redirect("order_success", order_id=order.id)

    return render(request, "orders/checkout.html", {
        "items": items,
        "total": total,
        "addresses": addresses,
    })
