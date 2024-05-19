from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required,user_passes_test

from accounts.forms import UserInformationUpdationForm, UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_for_customer
from django.contrib import messages
# Create your views here.

@login_required(login_url='login')
@user_passes_test(check_for_customer)
def customer_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        user_form = UserInformationUpdationForm(request.POST, instance=request.user)
        

        if user_profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            user_profile_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('customer_profile')
        else:
            print("User Profile Form Data:")
            for name, field in user_profile_form.fields.items():
                value = user_profile_form[name].value()
                errors = user_profile_form[name].errors
                print(f"Field: {name}, Value: {value}, Errors: {errors}")
            
            print("User Form Data:")
            for name, field in user_form.fields.items():
                value = user_form[name].value()
                errors = user_form[name].errors
                print(f"Field: {name}, Value: {value}, Errors: {errors}")
    else:
        user_profile_form = UserProfileForm(instance=user_profile)
        user_form = UserInformationUpdationForm(instance=request.user)

    context = {
        'user_profile_form':user_profile_form,
        'user_form':user_form,
        # 'user_profile':user_profile,
    }
    return render(request, 'customers/customer_profile.html', context)
