from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_wishlist, name='my_wishlist'),
    path('add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    
]
