from django.urls import path

from accounts import views

urlpatterns = [
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),
    path('login/', views.login, name='login'),
]