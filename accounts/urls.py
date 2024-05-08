from django.urls import path

from accounts import views

urlpatterns = [
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('myAccount/', views.myAccount, name='myAccount'),
    
    path('customerDashboard/', views.customerDashboard, name='customerDashboard'),
    path('vendorDashboard/', views.vendorDashboard, name='vendorDashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]