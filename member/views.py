from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import RegisterUserForm,EditProfileForm
from django.contrib.auth.models import User

def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=User.objects.get(email=email).username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')
        else:
            messages.success(request,"There was an error in logging in,try again!")
            return redirect('login')
    else:
        return render(request,'authenticate/login.html',{})

def logout_user(request):
    logout(request)
    messages.success(request, "You are logged out")
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,"Registration Successfull!")
            return redirect('home')
    else:
        form = RegisterUserForm()

    return render(request,'authenticate/register_user.html',{
        'form':form,
    })