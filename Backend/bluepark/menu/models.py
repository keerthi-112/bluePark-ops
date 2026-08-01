from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Menu(models.Model):
    item_name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')
    menuimg = models.ImageField(upload_to='menu-items-images')
    description = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.item_name
