from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_for_vendor
from menu.forms import CategoryForm
from menu.models import Category, FoodItem
from vendor.forms import VendorForm
from vendor.models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template.defaultfilters import slugify
from vendor.utils import get_vendor_object


# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_for_vendor)
def vendor_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if user_profile_form.is_valid() and vendor_form.is_valid():
            user_profile_form.save()
            vendor_form.save()
            messages.success(request, "Profile settings updated successfully..!")
            return redirect('vendor_profile')
        else:
            print(user_profile_form.errors)
            print(vendor_form.errors)
    else:
        user_profile_form = UserProfileForm(instance=user_profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'user_profile_form':user_profile_form,
        'vendor_form':vendor_form,
        'user_profile':user_profile,
        'vendor':vendor,
    }
    return render(request, 'vendor/vendor_profile.html', context)

@login_required(login_url='login')
@user_passes_test(check_for_vendor)
def menu_builder(request):
    vendor = get_vendor_object(request)
    categories = Category.objects.filter(vendor=vendor)
    context = {
        'categories':categories,
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_for_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor_object(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems':fooditems,
        'category':category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_for_vendor)
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            new_category = category_form.save(commit=False)
            new_category.vendor = get_vendor_object(request)
            new_category.slug = slugify(category_form.cleaned_data['category_name'])
            category_form.save()
            messages.success(request, "Category added successfully")
            return redirect('menu_builder')
    else:
        category_form = CategoryForm()
    context = {
        'category_form':category_form,
    }
    return render(request, 'vendor/add_category.html', context)
