from django.contrib import admin

from orders.models import Order, OrderedFood, Payment
# Register your models here.

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone_number', 'email', 'total', 'payment_method', 'order_placed_to', 'status', 'is_ordered']
    inlines = [OrderedFoodInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)