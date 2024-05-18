from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from marketplace.context_processors import get_cart_amounts, get_cart_counter
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import OpeningHour, Vendor
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    business_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    current_date = date.today()
    week_day = current_date.isoweekday()
    current_business_hours = OpeningHour.objects.filter(vendor=vendor, day=week_day)

    # current_time = datetime.now().strftime("%H:%M:%S")

    # is_open = False
    # for i in current_business_hours:
    #     open_time = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
    #     close_time = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

    #     if open_time <= current_time <= close_time:
    #         is_open = True
    #         break
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
        'business_hours':business_hours,
        'current_business_hours':current_business_hours,
        # 'is_open':is_open,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id=None):
    if request.method == 'GET':
        # Check if it's a Fetch request by inspecting the Content-Type header
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            # It's likely a Fetch request
            if request.user.is_authenticated:
                try:
                    fooditem = FoodItem.objects.get(id=food_id)
                    # Check if the user has already added food item to the cart
                    try:
                        check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                        check_cart.quantity += 1
                        check_cart.save()
                        return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity...!', 'cart_counter': get_cart_counter(request), 'qty': check_cart.quantity, 'cart_amount':  get_cart_amounts(request)})
                    except:
                        check_cart = Cart.objects.create(
                            user=request.user,
                            fooditem=fooditem,
                            quantity=1,
                        )
                        return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart...!', 'cart_counter': get_cart_counter(request), 'qty': check_cart.quantity, 'cart_amount':  get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed','message': 'Food item doesn\'t exists...!'})
            else:
                return JsonResponse({'status': 'login_required','message': 'Please login to your account....!'})
        else:
            # It's not a Fetch request
            return JsonResponse({'status': 'Failed','message': 'Invalid request type'})
    else:
        # Handle other types of requests
        return JsonResponse({'status': 'Fialed','message': 'Invalid request method'})
    
def decrease_in_cart(request, food_id):
    if request.method == 'GET':
        # Check if it's a Fetch request by inspecting the Content-Type header
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            # It's likely a Fetch request
            if request.user.is_authenticated:
                try:
                    fooditem = FoodItem.objects.get(id=food_id)
                    # Check if the user has already added food item to the cart
                    try:
                        check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                        if check_cart.quantity > 1:
                            check_cart.quantity -= 1
                            check_cart.save()
                        else:
                            check_cart.delete()
                            check_cart.quantity = 0
                        return JsonResponse({'status': 'Success',  'cart_counter': get_cart_counter(request), 'qty': check_cart.quantity, 'cart_amount':  get_cart_amounts(request)})
                    except:
                        return JsonResponse({'status': 'Failed', 'message': 'You do not have this food item in the cart...!'})
                except:
                    return JsonResponse({'status': 'Failed','message': 'Food item doesn\'t exists...!'})
            else:
                return JsonResponse({'status': 'login_required','message': 'Please login to your account....!'})
        else:
            # It's not a Fetch request
            return JsonResponse({'status': 'Failed','message': 'Invalid request type'})
    else:
        # Handle other types of requests
        return JsonResponse({'status': 'Fialed','message': 'Invalid request method'})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

def remove_item_from_cart(request, cart_id):
    if request.user.is_authenticated:
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success','message': 'Cart item deleted', 'cart_counter': get_cart_counter(request), 'cart_amount':  get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed','message': 'Cart item doesn\'t exists'})
        else:
            return JsonResponse({'status': 'Failed','message': 'Invalid request type'})

def search(request):
    if request.method == 'GET' and 'address' in request.GET:
        address = request.GET['address']
        latitude = request.GET['latitude']
        longitude = request.GET['longitude']
        radius = request.GET['radius']
        restaurant_food_name = request.GET['restaurant_food_name']

        # Get vendor ids that has the fooditem searched by user
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=restaurant_food_name, is_available=True).values_list('vendor', flat=True)
        vendors = Vendor.objects.filter (
            Q(id__in=fetch_vendors_by_fooditems) |
            Q(vendor_name__icontains=restaurant_food_name, is_approved=True, user__is_active=True)
        )

        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors = Vendor.objects.filter (
                Q(id__in=fetch_vendors_by_fooditems) |
                Q(vendor_name__icontains=restaurant_food_name, is_approved=True, user__is_active=True), 
                user_profile__location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for vendor in vendors:
                vendor.kms = round(vendor.distance.km, 2)
                
        number_of_vendors = vendors.count()
        context = {
            'vendors':vendors,
            'vendor_count':number_of_vendors,
            'source_location':address,
        }
        return render(request, 'marketplace/listings.html', context)
    else:
        return redirect('marketplace')