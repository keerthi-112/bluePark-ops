from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from menu import views

from core.constants import ROLE_ADMIN, ROLE_CHEF, ROLE_MANAGER, ROLE_WAITER

# Where each role lands right after login. Chef/Waiter point at 'home'
# until the Phase 1 kitchen queue view exists (Step 8), then switch to
# 'kitchen_queue'. Manager/Admin go to the Django admin until the
# Phase 3 manager dashboard exists.
ROLE_LANDING_PAGE = {
    ROLE_CHEF: 'home',
    ROLE_WAITER: 'home',
    ROLE_MANAGER: 'admin:index',
    ROLE_ADMIN: 'admin:index',
}


def login(request):
    if request.method=="POST":
        username = request.POST['uname']
        password = request.POST['pwd']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            landing = ROLE_LANDING_PAGE.get(user.profile.role, 'home')
            return redirect(landing)
        else:
            messages.info(request,'Invalid credentials')
            return redirect('login')
    else:
        return render(request,'login.html')

def register(request):
    if request.method=="POST":
        username = request.POST['uname']
        password1 = request.POST['pwd']
        password2 = request.POST['pwd1']
        email = request.POST['mail']
        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username already exists')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email already exists')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username,password=password1,email=email)
                user.save()
                messages.info(request,'Account Created Successfully')
                return redirect('register')
        else:
            messages.info(request,'Passwords are not matching..')
            return redirect('register')
    else:
        return render(request,'register.html')

def update(request):
    if request.method=="POST":
        username = request.POST['uname']
        password = request.POST['password']
        pwdnew = request.POST['pwd']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            user.set_password(raw_password=pwdnew)
            user.save()
            messages.info(request,'Password updated successfully..')
            return redirect('update')
        else:
            messages.info(request,'Invalid Credentials!')
            return redirect('update')
    else:
        return render(request,'update.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
