from django.http import HttpResponse
from django.shortcuts import redirect, render
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth

from accounts.utils import detectUser,send_verification_email
from vendor.forms import VendorForm

from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


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

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, "Your account has been registered successfully!. Please check your mail to activate your account")
            return redirect('myAccount')
        else:
            messages.error(request, "Account registration unsuccessful")
            context = {
                'user_form': user_form,
            }
            return render(request, 'accounts/registerCustomer.html', context)
    else:
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

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Your account has been registered successfully. Please check your mail to activate your account and wait for approval")
            return redirect('myAccount')
        else:
            print(user_form.errors)
            print(vendor_form.errors)
            messages.error(request, "Account registration unsuccessful")
            context = {
                'user_form': user_form,
                'vendor_form': vendor_form,
            }
            return render(request, 'accounts/registerVendor.html', context)
    else:
        user_form = UserForm()
        vendor_form = VendorForm()

    context = {
        'user_form': user_form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    # Activate the user by setting is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(ValueError, OverflowError, TypeError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations...!Your account has been activated now. Please login...!")
        return redirect('myAccount')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('myAccount')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send reset password email
            mail_subject = 'Reset your password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Password reset link has been sent to your registered email address")
            return redirect('myAccount')
        else:
            messages.error(request, "Account doesn't exists")
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    # Validate the user
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(ValueError, OverflowError, TypeError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Passwords updated successfully. Please login to your account")
            return redirect('myAccount')
        else:
            messages.error(request, "Passwords do not match!")
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

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
