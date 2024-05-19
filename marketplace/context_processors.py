from marketplace.models import Cart, Tax
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    
    return dict(cart_count=cart_count)

def get_cart_amounts(request):
    subtotal = 0
    final_tax_amount = 0
    grand_total = 0
    tax_dict = dict()

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity) 
        
        tax_objects = Tax.objects.filter(is_active=True)
        for i in tax_objects:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((subtotal * tax_percentage) / 100, 2)
            tax_dict.update({tax_type : { str(tax_percentage): tax_amount}})
            final_tax_amount += tax_amount
        
        grand_total = subtotal + final_tax_amount
        print(grand_total)
    return dict(subtotal=subtotal, final_tax_amount=final_tax_amount, grand_total=grand_total, tax_dict=tax_dict)