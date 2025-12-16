from django.contrib import admin
from .models import Profile, Address, Seller

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth', 'joined_at')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'country', 'is_default')
    list_filter = ('country', 'state', 'is_default')
    search_fields = ('full_name', 'city', 'postal_code')


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user', 'phone', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('store_name', 'user__username', 'phone')
    list_editable = ('is_approved',)