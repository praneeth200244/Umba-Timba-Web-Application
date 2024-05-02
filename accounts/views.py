from django.http import HttpResponse
from django.shortcuts import redirect, render
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages

from vendor.forms import VendorForm

# Create your views here.
def registerCustomer(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            password = user_form.cleaned_data['password']
            confirm_password = user_form.cleaned_data['confirm_password']
            user = user_form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "Your account has been registered successfully!. Please check your mail to activate your account")
            return redirect('login')
        else:
            messages.error(request, "Account registration unsuccessful")
            
    user_form = UserForm()
    context = {
        'user_form':user_form,
    }
    return render(request, 'accounts/registerCustomer.html', context)

def registerVendor(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)

        if user_form.is_valid() and vendor_form.is_valid():
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            phone_number = user_form.cleaned_data['phone_number']
            email = user_form.cleaned_data['email']
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                phone_number=phone_number,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save() 

            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.user_profile = UserProfile.objects.get(user=user)
            vendor.save()

            messages.success(request, "Your account has been registered successfully. Please wait for the approval")
            return redirect('login')
        else:
            messages.error(request, "Account registration unsuccessful")

    user_form = UserForm()
    vendor_form = VendorForm
    context = {
        'user_form': user_form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/registerVendor.html', context)

def login(request):
    return render(request, 'accounts/login.html')
