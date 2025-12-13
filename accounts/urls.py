from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    path("add-address/", views.add_address, name="add_address"),
    path("addresses/", views.address_list, name="address_list"),
    path("edit-address/<int:id>/", views.edit_address, name="edit_address"),
    path("delete-address/<int:id>/", views.delete_address, name="delete_address"),
    path("set-default/<int:id>/", views.set_default_address, name="set_default_address"),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),



]
