import simplejson as json
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required

from accounts.utils import send_notification_email
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number, order_total_by_vendor
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

# Create your views here.
@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_items_count = cart_items.count()
    if cart_items_count <= 0:
        return redirect('marketplace')
    
    # Get unique vendor IDs
    vendor_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendor_ids:
            vendor_ids.append(i.fooditem.vendor.id)
    
    tax_objects = Tax.objects.filter(is_active=True)
    subtotal = 0
    vendor_ids_dict = {}
    total_data = {}
    for item in cart_items:
        fooditem = FoodItem.objects.get(pk=item.fooditem.id, vendor_id__in=vendor_ids)
        v_id = fooditem.vendor.id 
        if v_id in vendor_ids_dict:
            subtotal = vendor_ids_dict[v_id]
            subtotal += (fooditem.price * item.quantity)
            vendor_ids_dict[v_id] = subtotal
        else:
            subtotal = (fooditem.price * item.quantity)
            vendor_ids_dict[v_id] = subtotal

        # Tax data
        tax_dict = {}
        for i in tax_objects:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((subtotal * tax_percentage) / 100, 2)
            tax_dict.update({tax_type : { str(tax_percentage): str(tax_amount)}})
        total_data.update({fooditem.vendor.id : {str(subtotal) : str(tax_dict) }})
    
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
            order.total_data = json.dumps(total_data)
            order.total_tax = final_tax_amount
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendor_ids) # Addding ManyToManyField data '*' is used to recursively add data to the field
            order.save()
            context = {
                'cart_items':cart_items,
                'order': order,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(order_form.errors)
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
@csrf_protect
def payments(request):
    if request.method == 'POST':
        # Check if it's a Fetch request by inspecting the Content-Type header
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            if request.user.is_authenticated:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                    transaction_id = data.get('transaction_id')
                    order_number = data.get('order_number')
                    payment_method = data.get('payment_method')
                    status = data.get('status')
                except:
                    return JsonResponse({'status':'error', 'message': 'Error Occured'})
                order = Order.objects.get(user=request.user, order_number=order_number)

                # Store the payment details in payment model
                payment = Payment(
                    user = request.user,
                    transaction_id = transaction_id,
                    payment_method = payment_method,
                    amount = order.total,
                    status = status,
                )
                payment.save()

                # Update the order model
                order.payment = payment
                order.is_ordered = True
                order.save()
            
                # Move the cart items into ordered food model
                cart_items = Cart.objects.filter(user=request.user)
                for item in cart_items:
                    ordered_food = OrderedFood()
                    ordered_food.order = order
                    ordered_food.payment = payment
                    ordered_food.user = request.user
                    ordered_food.fooditem = item.fooditem
                    ordered_food.quantity = item.quantity
                    ordered_food.price = item.fooditem.price
                    ordered_food.amount = item.fooditem.price * item.quantity
                    ordered_food.save()


                # Send order confirmation email to the customer
                mail_subject = 'Thank you for ordering with us'
                mail_template = 'orders/order_confirmation_customer_email.html'
                ordered_food = OrderedFood.objects.filter(order=order)
                customer_subtotal = 0
                for item in ordered_food:
                    customer_subtotal += (item.price * item.quantity)
                tax_dict = json.loads(order.tax_data)
                context = {
                    'user':request.user,
                    'order':order,
                    'ordered_food':ordered_food,
                    'to_email' : order.email,
                    'domain': get_current_site(request),
                    'customer_subtotal':customer_subtotal,
                    'tax_data':tax_dict,
                }
                send_notification_email(mail_subject, mail_template, context)

                # Send order received email to the vendor
                mail_subject = 'You have received a new order'
                mail_template = 'orders/new_order_vendor_email.html'
                to_email = []
                for cart_item in cart_items:
                    if cart_item.fooditem.vendor.user.email not in to_email:
                        to_email.append(cart_item.fooditem.vendor.user.email)

                        ordered_food_from_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=cart_item.fooditem.vendor)
                        order_total_by_vendor_email = order_total_by_vendor(order, cart_item.fooditem.vendor.id)
                        context = {
                            'user':request.user,
                            'order':order,
                            'to_email' : cart_item.fooditem.vendor.user.email,
                            'ordered_food_from_vendor':ordered_food_from_vendor,
                            'vendor_subtotal':order_total_by_vendor_email['subtotal'],
                            'vendor_grand_total':order_total_by_vendor_email['grand_total'],
                            'tax_data':order_total_by_vendor_email['tax_dict'],
                        }
                        send_notification_email(mail_subject, mail_template, context)

                # Clear the cart if the payment is success
                cart_items.delete()

                # Return JsonResponse
                response = {
                    'status': 'success',
                    'message': 'Order placed Successfully',
                    'order_number':order_number,
                    'transaction_id': transaction_id,
                }
                return JsonResponse(response)
            else:
                return JsonResponse({'status': 'Failed', 'message': 'Authentication Issues'})
        else:
            return JsonResponse({'status':'failed', 'message':'Invalid request type'})
    else:
            return JsonResponse({'status':'failed', 'message':'Invalid request method'})
            
def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        sub_total = 0
        for item in ordered_food:
            sub_total += (item.price * item.quantity)
        
        tax_data = json.loads(order.tax_data)

        context = {
            'order':order,
            'ordered_food':ordered_food,
            'sub_total':sub_total,
            'tax_data':tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
    