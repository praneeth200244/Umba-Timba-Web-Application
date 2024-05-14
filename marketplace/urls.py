from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # ADD TO CART
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # DECREASE ITEM IN CART
    path('decrease_in_cart/<int:food_id>/', views.decrease_in_cart, name='decrease_in_cart'),

    # DELETE ITEM FROM CART
    path('remove_item_from_cart/<int:cart_id>/', views.remove_item_from_cart, name='remove_item_from_cart'),
]
