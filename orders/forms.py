from django import forms

from orders.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone_number', 'alternate_phone_number', 'address', 'country', 'state', 'city', 'pin_code']