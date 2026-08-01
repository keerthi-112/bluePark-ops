from django.shortcuts import render
from accounts import views
from survey import views
from checkout import views
from .models import Menu

# Create your views here.
def home(request):
    menu_items = Menu.objects.all()
    return render(request,'homepage.html',{'menu_items':menu_items})

