from django.urls import path, include
from accounts import views as AccountViews
from vendor import views

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendorDashboard'),
    path('profile', views.vendor_profile, name='vendor_profile'),
    path('menu-builder', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
]