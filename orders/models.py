from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from accounts.models import Address

# Payment Model
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('COD', 'Cash On Delivery'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('NETBANK', 'Net Banking'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.method} - {self.status}"


# Order Model
class Order(models.Model):
    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Address reference 
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    # Store snapshot so old orders are safe even if user deletes address
    shipping_full_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_phone = models.CharField(max_length=15, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)

    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"



# Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    def get_subtotal(self):
        return self.price * self.quantity


# Shipment Model
class Shipment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ('PLACED', 'Order Placed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    )

    tracking_no = models.CharField(max_length=100, unique=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PLACED')
    return_status = models.CharField(max_length=20, default="NONE")


