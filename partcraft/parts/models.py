from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    STATUS_CHOICES = (
        ('petrol', 'petrol'),
        ('diesel', 'diesel')
    )
    vehicle_name = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    vehicle_type = models.CharField(choices=STATUS_CHOICES, max_length=50)

    def __str__(self):
        return f'{self.vehicle_name} {self.vehicle_model} {self.vehicle_year} {self.vehicle_type}'


class Brand(models.Model):
    brand_name = models.CharField(max_length=50)
    brand_image = models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.brand_name


class Category(models.Model):
    category_name = models.CharField(max_length=50)
    category_image = models.ImageField(upload_to='categories/',blank=True)

    def __str__(self):
        return self.category_name


class Product(models.Model):
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
    main_image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f'{self.parts_brand}-{self.parts_category}-{self.subcategory_name}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f'{self.product.subcategory_name} - {self.id}'


class Wishlist(models.Model):
    wishlist_name=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wishlist_product=models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.wishlist_name} {self.wishlist_product}'



class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.user} {self.product} {self.quantity}'