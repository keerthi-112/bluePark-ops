from django.shortcuts import render
from .models import Cart, Cart_items, Orders
from django.http import JsonResponse
#from django.views.generic import ListView, View


# Create your views here.
def cart_add(request):
    login = request.GET.get('login',None)
    count = request.GET.get('count',None)
    #if login==1 and count==0:
    Cart.objects.create(total=0)
    
    item_name = request.GET.get('title',None)
    price = request.GET.get('price',None)
    obj = Cart_items.objects.create(cart_id=Cart.cart_id,item_name=item_name,price=price,quantity=1)
    obj.save()
    data = {'cartid':cobj }
    return JsonResponse(data)

    

def cart_update(request):
    pass

#def cart_del(request):

#def cart_edit(request):