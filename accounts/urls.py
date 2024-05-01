from django.urls import path

from accounts import views

urlpatterns = [
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('login/', views.login, name='login'),
]