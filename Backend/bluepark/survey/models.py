from django.db import models

# Create your models here.
class Survey_feedback(models.Model):
    source = models.CharField(max_length=14)
    name = models.CharField(max_length=40)
    purchase = models.BooleanField()
    favourite_food = models.CharField(max_length=100)
    mail = models.EmailField(max_length=30)
    rating = models.PositiveSmallIntegerField()
    feed = models.CharField(max_length=300)
    