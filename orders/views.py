import simplejson as json
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.models import Order
from orders.utils import generate_order_number

# Create your views here.
@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_items_count = cart_items.count()
    if cart_items_count <= 0:
        return redirect('marketplace')
    
    subtotal = get_cart_amounts(request)['subtotal']
    final_tax_amount = get_cart_amounts(request)['final_tax_amount']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = Order()
            order.first_name = order_form.cleaned_data['first_name']
            order.last_name = order_form.cleaned_data['last_name']
            order.email = request.user.email
            order.phone_number = order_form.cleaned_data['phone_number']
            order.alternate_phone_number = order_form.cleaned_data['alternate_phone_number']
            order.address = order_form.cleaned_data['address']
            order.city = order_form.cleaned_data['city']
            order.state = order_form.cleaned_data['state']
            order.country = order_form.cleaned_data['country']
            order.pin_code = order_form.cleaned_data['pin_code']

            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = final_tax_amount
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
    return render(request, 'orders/place_order.html')