from django.db import models
from django.contrib.auth.models import User, auth
#import uuid

# Create your models here.
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True, unique=True)
    total = models.PositiveIntegerField()

class Cart_items(models.Model):
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item_id = models.AutoField(primary_key=True, unique=True)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveSmallIntegerField()
    note = models.CharField(max_length=250, blank=True)
    price = models.PositiveSmallIntegerField()

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, unique=True)
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=350)
    mobile = models.CharField(max_length=12)

