from django.contrib import admin
from .models import Payment, Order, OrderItem, Shipment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'amount', 'status', 'created_at')
    list_filter = ('method', 'status')
    search_fields = ('payment_id',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'tracking_no', 'status', 'shipped_date', 'delivery_date')