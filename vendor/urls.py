from django.urls import path, include
from accounts import views as AccountViews
from vendor import views

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendorDashboard'),
    path('profile', views.vendor_profile, name='vendor_profile'),
]