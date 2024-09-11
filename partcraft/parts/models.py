from itertools import product
from django.db import models
from django.conf import settings
import os
import uuid
from datetime import datetime
import random
class Vehicle(models.Model):
    STATUS_CHOICES = (
        ('petrol', 'petrol'),
        ('diesel', 'diesel')
    )
    vehicle_name = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    vehicle_variant = models.CharField(choices=STATUS_CHOICES, max_length=50)

    def __str__(self):
        return f'{self.vehicle_name} {self.vehicle_model} {self.vehicle_year} {self.vehicle_variant}'


class Brand(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_image = models.URLField(max_length=200)

    def __str__(self):
        return self.brand_name


class Category(models.Model):
    category_name = models.CharField(max_length=50)
    category_image = models.URLField(max_length=200,blank=True)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    objects = None
    TYPE_CHOICES = (
        ('OE', 'OE'),
        ('AFTERMARKET', 'AFTERMARKET'),
    )
    STATUS_CHOICES = (
        ('in stock', 'in stock'),
        ('out of stock', 'out of stock'),
    )
    CONDITION_CHOICES = (
        ('New','New'),
        ('Refurbished','Refurbished'),
    )


    parts_brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    parts_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=255)
    parts_voltage = models.IntegerField()
    parts_fits = models.CharField(max_length=255,blank=True)
    parts_litre = models.FloatField(blank=True, null=True)
    parts_type = models.CharField(choices=TYPE_CHOICES, max_length=255)
    parts_description = models.TextField()
    parts_no= models.CharField(max_length=255)
    parts_price = models.IntegerField(default=0)
    parts_offer= models.IntegerField()
    parts_status = models.CharField(choices=STATUS_CHOICES, max_length=255)
    parts_condition = models.CharField(choices=CONDITION_CHOICES, max_length=255)
    parts_warranty= models.IntegerField()
    parts_specification=models.TextField()
    this_parts_fits=models.ManyToManyField(Vehicle)
    main_image = models.URLField(max_length=200)

    def __str__(self):
        return f'{self.parts_brand}-{self.parts_category}-{self.subcategory_name}'


class RelatedProduct(models.Model):
    related_product1 = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='related_product1_set')
    related_product2 = models.ManyToManyField(Product,related_name='related_product2_set')
    retated_type = models.CharField(max_length=255)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.URLField(max_length=200)

    def __str__(self):
        return f'{self.product.subcategory_name} - {self.id}'


class Wishlist(models.Model):
    wishlist_name=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wishlist_product=models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.wishlist_name} {self.wishlist_product}'


class Carousel(models.Model):
    carousel_image=models.URLField(max_length=200)
    carousel_offer=models.IntegerField(default=0)
    carousel_category= models.ForeignKey(Category, on_delete=models.CASCADE)
    carousel_code=models.CharField(max_length=255)
    carousel_brand=models.ForeignKey(Brand, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.carousel_code} {self.carousel_offer}'

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    code=models.ManyToManyField(Carousel,blank=True)

    def __str__(self):
        return f'{self.user} {self.product} {self.quantity}'


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    billing_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=16, blank=True, null=True)
    email = models.EmailField(max_length=255)
    billing_address = models.CharField(max_length=1000)
    city = models.CharField(max_length=255, blank=True, null=True)
    #contact = models.CharField(max_length=13, blank=True, null=True)


    def __str__(self):
        return f'{self.billing_name} {self.billing_address}'

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    shipping_address = models.CharField(max_length=1000)
    city = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=13)
    use_the_address_for_next_time = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.shipping_name} {self.shipping_address}'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferred_billing_address = models.ForeignKey(BillingAddress, null=True, blank=True, on_delete=models.SET_NULL, related_name='preferred_billing_user')
    preferred_shipping_address = models.ForeignKey(ShippingAddress, null=True, blank=True, on_delete=models.SET_NULL, related_name='preferred_shipping_user')
    def __str__(self):
        return f"Profile for {self.user}"


def order_gen_id():
    timestamp = datetime.now().strftime('%m%d%Y')
    num = random.randint(100000, 999999)
    return f'{timestamp}_{num}'

class Order(models.Model):
    STATUS_CHOICES = [
        ('InProgress', 'InProgress'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    billing_address = models.ForeignKey(BillingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=20, unique=True)
    order_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    status = models.CharField(choices=STATUS_CHOICES, max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.order_id} {self.product}'

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = order_gen_id()
        super(Order, self).save(*args, **kwargs)

class ProductOrderCount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.product} - {self.order_count}'


class Feedback(models.Model):
    name=models.CharField(max_length=255)
    company_name=models.CharField(max_length=255)
    designation=models.CharField(max_length=255)
    email=models.EmailField(max_length=255)
    image=models.URLField(max_length=200)
    feedback=models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name} {self.company_name} {self.designation} {self.email} {self.image}'

class DealerAddress(models.Model):
    name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=16, blank=True, null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    def __str__(self):
        return f'{self.name} {self.address} {self.city} {self.email}'



