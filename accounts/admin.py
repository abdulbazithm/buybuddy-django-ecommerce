from django.contrib import admin
from .models import Profile, Address

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth', 'joined_at')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'country', 'is_default')
    list_filter = ('country', 'state', 'is_default')
    search_fields = ('full_name', 'city', 'postal_code')

