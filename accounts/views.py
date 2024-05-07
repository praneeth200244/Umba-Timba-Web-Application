from django.http import HttpResponse
from django.shortcuts import redirect, render
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth

from accounts.utils import detectUser
from vendor.forms import VendorForm

from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied

# Restrict the vendor from accessing the customer page
def check_for_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict the customer from accessing the vendor page
def check_for_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

# Create your views here.
def registerCustomer(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myAccount')
    elif request.method == 'POST':
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
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myAccount')
    elif request.method == 'POST':
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
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect('myAccount')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
        
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out!")
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    redirectUrl = detectUser(request.user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_for_customer)
def customerDashboard(request):
    return render(request, 'accounts/customerDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_for_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')
