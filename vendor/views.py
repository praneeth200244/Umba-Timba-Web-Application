from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_for_vendor
from vendor.forms import VendorForm
from vendor.models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test


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