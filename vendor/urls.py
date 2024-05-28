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
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Food Item CRUD
    path('menu-builder/food/add/', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>/', views.delete_food, name='delete_food'),

    # OPENING HOUR CRUD
    path('business-hours/', views.business_hours, name='business_hours'),
    path('business-hours/add/', views.add_business_hours, name='add_business_hours'),
    path('business-hours/delete/<int:pk>', views.remove_business_hours, name='remove_business_hours'),

    path('order_details/<int:order_number>/', views.vendor_order_details, name='vendor_order_details'),
    path('my_orders/', views.vendor_my_orders, name='vendor_my_orders'),
]