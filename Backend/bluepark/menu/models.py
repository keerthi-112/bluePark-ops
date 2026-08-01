from django.db import models

# Create your models here.
class Menu(models.Model):
    item_name = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    menuimg = models.ImageField(upload_to='menu-items-images')
    description = models.CharField(max_length=80)
    price = models.PositiveSmallIntegerField()

#class Cart(models.Model):
    