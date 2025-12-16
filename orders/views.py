from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.db import transaction
from django.contrib import messages

from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from cart.models import Cart
from accounts.models import Address
from .models import Order, OrderItem, Payment, Shipment




# ---------------------------------------------------------
# CHECKOUT PAGE  (Step 1)
# ---------------------------------------------------------
@login_required
def checkout(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    items = cart.items.all()
    total = cart.get_total()
    addresses = Address.objects.filter(user=user)

    if not items.exists():
        return redirect("view_cart")

    if request.method == "POST":
        address_id = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect("checkout")

        # Save temporary session values
        request.session["checkout_address"] = address_id
        request.session["checkout_payment"] = payment_method

        # COD → direct order
        if payment_method == "COD":
            return redirect("place_order")

        # Online payment
        return redirect("payment_page")

    return render(request, "orders/checkout.html", {
        "items": items,
        "total": total,
        "addresses": addresses,
    })


# ---------------------------------------------------------
# PAYMENT PAGE (Online only, Step 2)
# ---------------------------------------------------------
@login_required
def payment_page(request):
    method = request.session.get("checkout_payment")
    address_id = request.session.get("checkout_address")

    if not method or not address_id:
        return redirect("checkout")

    # COD → Skip
    if method == "COD":
        return redirect("place_order")

    cart = get_object_or_404(Cart, user=request.user)
    amount = cart.get_total()   # correct amount, NOT paisa

    if request.method == "POST":
        # Fake payment ID
        fake_payment_id = "PAY_" + get_random_string(12).upper()

        # Store in session temporarily
        request.session["dummy_payment_id"] = fake_payment_id

        print("Dummy Payment Success - Mode:", method)
        print("Dummy Payment ID:", fake_payment_id)

        return redirect("place_order")

    return render(request, "orders/payment_page.html", {
        "method": method,
        "amount": amount
    })


# ---------------------------------------------------------
# PLACE ORDER (Final Step)
# ---------------------------------------------------------
@login_required
def place_order(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    items = cart.items.all()

    if not items.exists():
        return redirect("view_cart")

    address_id = request.session.get("checkout_address")
    payment_method = request.session.get("checkout_payment")

    if not address_id or not payment_method:
        return redirect("checkout")

    address = get_object_or_404(Address, id=address_id, user=user)
    total = cart.get_total()

    with transaction.atomic():

        # 1. Payment entry
        fake_pid = request.session.get("dummy_payment_id", "PAY_OFFLINE")
        payment = Payment.objects.create(
            user=user,
            method=payment_method,
            amount=total,
            payment_id=fake_pid,
            status="Completed"
        )

        # 2. Order entry WITH SHIPPING SNAPSHOT
        order = Order.objects.create(
            user=user,
            address=address,
            payment=payment,
            total_amount=total,
            status="PENDING",

            # 📌 SNAPSHOT: Store address details at the time of order
            shipping_full_name=address.full_name,
            shipping_phone=address.phone,
            shipping_address=address.full_address(),
        )

        # 3. Order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        # 4. Shipment
        Shipment.objects.create(
            order=order,
            tracking_no="BB" + get_random_string(8).upper(),
            courier_name="BuyBuddy Express",
            status="Preparing for dispatch"
        )

        # 5. Clear cart
        items.delete()

        # 6. Clear sessions
        request.session.pop("checkout_address", None)
        request.session.pop("checkout_payment", None)
        request.session.pop("dummy_payment_id", None)

    return redirect("order_success", order_id=order.id)


# ---------------------------------------------------------
# ORDER SUCCESS PAGE
# ---------------------------------------------------------
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})



# ---------------------------------------------------------
# CANCEL ORDERS
# ---------------------------------------------------------
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Prevent cancelling delivered or already cancelled
    if order.status in ["DELIVERED", "CANCELLED"]:
        messages.error(request, "This order cannot be cancelled.")
        return redirect("order_detail", order_id=order_id)

    with transaction.atomic():
        # 1. Update order status
        order.status = "CANCELLED"
        order.save()

        # 2. Refund for online payments
        if order.payment.method != "COD":
            order.payment.status = "Refunded"
            order.payment.save()

        # 3. Restore product stock (optional)
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        # 4. Update shipment
        order.shipment.status = "Order Cancelled"
        order.shipment.save()

    messages.success(request, "Your order has been cancelled.")
    return redirect("order_detail", order_id=order_id)



# ---------------------------------------------------------
# LIST ALL ORDERS
# ---------------------------------------------------------
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


# ---------------------------------------------------------
# SHOW A SINGLE ORDER
# ---------------------------------------------------------
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    tracking_stages = ['PLACED', 'PROCESSING', 'SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'tracking_stages': tracking_stages
    })



# ---------------------------------------------------------
# DOWLOAD ORDERS INVOICE
# ---------------------------------------------------------
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # File response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 50, "BUYBUDDY - OFFICIAL INVOICE")

    p.setFont("Helvetica", 12)
    p.drawString(30, height - 90, f"Invoice No: BB-INV-{order.id}")
    p.drawString(30, height - 110, f"Order Date: {order.created_at.strftime('%Y-%m-%d')}")
    p.drawString(30, height - 130, f"Customer: {order.user.username}")
    p.drawString(30, height - 150, f"Payment Method: {order.payment.method}")
    p.drawString(30, height - 170, f"Payment Status: {order.payment.status}")

    # Address
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, height - 210, "Shipping Address:")
    p.setFont("Helvetica", 12)
    p.drawString(30, height - 230, order.address.full_address())

    # Items table
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, height - 270, "Order Items:")

    y = height - 300
    p.setFont("Helvetica", 12)

    for item in order.items.all():
        p.drawString(30, y, f"{item.product.name} (x{item.quantity}) - Rs {item.price}")
        y -= 20

    # Total
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, y - 20, f"Total Amount: Rs {order.total_amount}")

    p.showPage()
    p.save()
    return response


@login_required
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Make sure order has shipment
    if not hasattr(order, "shipment"):
        messages.error(request, "Shipment information not available.")
        return redirect('order_detail', order_id=order.id)

    shipment = order.shipment

    # Return only after delivery
    if shipment.status != "DELIVERED":
        messages.error(request, "You can request a return only after delivery.")
        return redirect('order_detail', order_id=order.id)

    # Already requested
    if shipment.return_status == "REQUESTED":
        messages.info(request, "Return already requested.")
        return redirect('order_detail', order_id=order.id)

    if request.method == "POST":
        shipment.return_status = "REQUESTED"
        shipment.save()

        messages.success(request, "Return request submitted successfully!")
        return redirect('order_detail', order_id=order.id)

    return render(request, "orders/return_confirm.html", {
        "order": order,
        "shipment": shipment,
    })


def track_order(request, tracking_id):
    shipment = get_object_or_404(Shipment, tracking_no=tracking_id)
    order = shipment.order

    return render(request, "orders/track_order.html", {
        "order": order,
        "shipment": shipment
    })


