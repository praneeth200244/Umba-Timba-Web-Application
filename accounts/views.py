from django.http import HttpResponse
from django.shortcuts import redirect, render
from accounts.forms import UserForm
from accounts.models import User
from django.contrib import messages

# Create your views here.
def registerCustomer(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            password = user_form.cleaned_data['password']
            confirm_password = user_form.cleaned_data['confirm_password']
            if password == confirm_password:
                user = user_form.save(commit=False)
                user.set_password(password)
                user.role = User.CUSTOMER
                user.save()
                return redirect('login')
            
    user_form = UserForm()
    context = {
        'user_form':user_form,
    }
    return render(request, 'accounts/registerCustomer.html', context)

def login(request):
    return render(request, 'accounts/login.html')
