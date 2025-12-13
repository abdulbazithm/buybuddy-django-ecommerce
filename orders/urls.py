from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    path('payment/', views.payment_page, name="payment_page"),
    path('place-order/', views.place_order, name="place_order"),
    path("track/<str:tracking_id>/", views.track_order, name="track_order"),
    path('order/<int:order_id>/cancel/', views.cancel_order, name="cancel_order"),
    path('order/<int:order_id>/invoice/', views.download_invoice, name='download_invoice'),
    path('order/<int:order_id>/return/', views.return_order, name='return_order'),

   



    

 

]
