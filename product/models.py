from django.db import models
from users import models as users_models

# Create your models here.


user = users_models.CustomUser()

class Category(models.TextChoices):
    Computers = 'Computers'
    Food = 'Food'
    Kids = 'Kids'
    Home = 'Home'

class Item(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="", blank=False)
    description = models.TextField(max_length=1000, default="", blank=False)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    discount_price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    brand = models.CharField(max_length=200, default="", blank=False)
    category = models.CharField(max_length=200, choices=Category.choices)
    rating = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_final_item_price(self):
        if self.discount_price is not None:
            return int(self.price - self.discount_price)
        else:
            return self.price




class OrderItem(models.Model):
    user = models.ForeignKey(users_models.CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.item.price * self.quantity
    
    def get_total_discount_item_price(self):
        return (self.item.price - self.item.discount_price) * self.quantity
    
    
    def get_amount_saved(self):
        return (self.item.discount_price) * self.quantity
    

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        else:
            return self.get_total_item_price()
        


class ORDERSTATUS(models.TextChoices):
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"


class PAYMENTSTATUS(models.TextChoices):
    PAID = "Paid"
    UNPAID = "UnPaid"


class PAYMENTMETHOD(models.TextChoices):
    COD = "COD"
    CARD = "CARD"



class Order(models.Model):
    user = models.ForeignKey(users_models.CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(OrderItem)
    address = models.CharField(max_length=500, null=False, blank=False)
    phone_number = models.CharField(max_length=11, null=False, blank=False)
    payment_status = models.CharField(max_length=50, choices=PAYMENTSTATUS, default=PAYMENTSTATUS.UNPAID)
    payment_method = models.CharField(max_length=50, choices=PAYMENTMETHOD, default=PAYMENTMETHOD.COD)
    order_status = models.CharField(max_length=50, choices=ORDERSTATUS, default=ORDERSTATUS.PROCESSING)
    total_amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    done_ordered_time = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_items(self):
        total_items = 0
        for order_item in self.items.all():
            total_items += order_item.quantity
        return total_items







class Review(models.Model):
    item = models.ForeignKey(Item, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(user, null=True, on_delete=models.SET_NULL)
    rating = models.PositiveIntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}"