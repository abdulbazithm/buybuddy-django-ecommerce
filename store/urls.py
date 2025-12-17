from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),

    path('add-review/<int:order_item_id>/', views.add_review, name="add_review"),

    path("review/edit/<int:review_id>/", views.edit_review, name="edit_review"),
    path("review/delete/<int:review_id>/", views.delete_review, name="delete_review"),


    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path("category/<slug:category_slug>/", views.category_products, name="category_products"),
    path("search/", views.search_products, name="search"),




 

]
