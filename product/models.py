from django.db import models
from users import models as users_models

# Create your models here.


user = users_models.CustomUser()

class Category(models.TextChoices):
    Computers = 'Computers'
    Food = 'Food'
    Kids = 'Kids'
    Home = 'Home'

class Product(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="", blank=False)
    description = models.TextField(max_length=1000, default="", blank=False)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    brand = models.CharField(max_length=200, default="", blank=False)
    category = models.CharField(max_length=200, choices=Category.choices)
    rating = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"




class Review(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(user, null=True, on_delete=models.SET_NULL)
    rating = models.PositiveIntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"