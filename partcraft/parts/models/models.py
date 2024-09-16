from itertools import product
from django.db import models
from django.conf import settings
import os
import uuid
from datetime import datetime
from account.models import Cost_Code
import random
from account.models import User
from django.core.exceptions import ValidationError
# from djongo import models as djongo_models
# import mongoengine as me


class Manufacturer(models.Model):
    name = models.CharField(max_length=50,unique=True)
    is_vehicle_manufacturer = models.BooleanField(default=False)
    is_product_manufacturer = models.BooleanField(default=False)
    logo = models.URLField()

    def __str__(self):
        return self.name

class Application_type(models.Model):
    type_name = models.CharField(max_length=100)
    def __str__(self):
        return self.type_name
class Application_category(models.Model):
    type_name = models.ForeignKey(Application_type, on_delete=models.CASCADE)
    category_name = models.CharField(verbose_name="categories_name", max_length=100)
    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Application_category'


class Vehicle(models.Model):
    vehicle_category = models.ForeignKey(verbose_name='Application_category', to=Application_category, on_delete=models.CASCADE, default=1)
    vehicle_make = models.ForeignKey(verbose_name='make', to=Manufacturer, on_delete=models.CASCADE, limit_choices_to={'is_vehicle_manufacturer': True})
    vehicle_model = models.CharField(verbose_name='model', max_length=500)
    vehicle_year = models.IntegerField(verbose_name='year')
    vehicle_variant = models.CharField(verbose_name='variant', max_length=500, blank=True)

    def __str__(self):
        return f'{self.vehicle_make} {self.vehicle_model} {self.vehicle_year} {self.vehicle_variant}'
    class Meta:
        db_table = 'Application'
        verbose_name = 'Application'


# class Brand(models.Model):
#     brand_name = models.CharField(max_length=50)
#     brand_image = models.URLField(max_length=200)
#
#     def __str__(self):
#         return self.brand_name


class Brand(models.Model):
    brand_manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE,limit_choices_to=({'is_product_manufacturer': True}))

    def __str__(self):
        return f"{self.brand_manufacturer.name}, {self.brand_manufacturer.logo}"
    class Meta:
        verbose_name = 'Product Brand'

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    category_image = models.URLField(max_length=200,blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'Product Categories'

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

    product_code=models.CharField(max_length=10)
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
        return self.product_code


class RelatedProduct(models.Model):
    STATUS_CHOICES = (
        ('similar', 'similar'),
        ('related', 'related'),
    )
    related_product1 = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='related_product1_set')
    related_product2 = models.ManyToManyField(Product,related_name='related_product2_set')
    retated_type = models.CharField(choices=STATUS_CHOICES, max_length=255)
    Isbidirectional = models.BooleanField()

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
    tin = models.CharField(max_length=16, blank=True, null=True)
    email = models.EmailField(max_length=255)
    billing_address = models.CharField(max_length=1000)
    # city = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return f'{self.billing_name} {self.billing_address}'

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    shipping_address = models.CharField(max_length=1000)
    contact = models.CharField(max_length=13)


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
    # email=models.EmailField(max_length=255, blank=True, null=True)
    image=models.FileField(max_length=200)
    feedback=models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name} {self.company_name} {self.designation} {self.email} {self.image}'

# class DealerAddress(models.Model):
#     name = models.CharField(max_length=255)
#     gst_number = models.CharField(max_length=16, blank=True, null=True)
#     address = models.CharField(max_length=255)
#     city = models.CharField(max_length=255)
#     email = models.EmailField(max_length=255)
#     phone = models.CharField(max_length=255)
#     def __str__(self):
#         return f'{self.name} {self.address} {self.city} {self.email}'


class SellerGroup(models.Model):
    group = models.CharField(max_length=255)

    def __str__(self):
        return self.group

class Seller(models.Model):
    TYPE_CHOICES = [
        ('Manufacturer', 'Manufacturer'),
        ('Dealer', 'Dealer'),
    ]
    name = models.CharField(max_length=255)
    seller_type = models.CharField(choices=TYPE_CHOICES, max_length=255)
    group = models.ForeignKey(SellerGroup, on_delete=models.CASCADE)
    tin = models.CharField(max_length=20)
    address = models.CharField(max_length=1023)
    email = models.EmailField(max_length=255)
    mobile_no = models.CharField(max_length=10)
    def __str__(self):
        return f'{self.name} {self.address}'

class Product_cost(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_cost = models.IntegerField(default=0)
    product_currency = models.CharField(max_length=255)#model
    cost_code=models.ForeignKey(Cost_Code, on_delete=models.CASCADE,default=1)
    effective_from=models.DateTimeField()
    def __str__(self):
        return f'{self.product_id} {self.product_cost} {self.product_currency}'

class Product_btc_partners(models.Model):
    partner_name = models.CharField(max_length=255)
    partner_logo = models.URLField(max_length=511)

class Product_btc_links(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bzc_partner = models.ForeignKey(Product_btc_partners, on_delete=models.CASCADE)
    url = models.URLField(max_length=511)

class MerchandisingSlot(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, unique=True, null=False)
    width = models.IntegerField(null=False)
    height = models.IntegerField(null=False)
    Aspect_ratio_threshold = models.IntegerField(default=10)

class MerchandisingContent(models.Model):
    LINK_TYPE_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External')
    ]
    id = models.AutoField(primary_key=True)
    slot = models.ForeignKey(MerchandisingSlot, on_delete=models.CASCADE, null=False)
    image_url = models.URLField(max_length=510, null=True, blank=True)
    # image_storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    click_link = models.CharField(max_length=255, null=True, blank=True)
    click_link_type = models.CharField(choices=LINK_TYPE_CHOICES,max_length=255, null=False)

class Tags(models.Model):
    ID=models.CharField(max_length=255,primary_key=True)
    tag_name=models.CharField(max_length=255,unique=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.tag_name

class ProductTags(models.Model):
    ID=models.CharField(max_length=255,primary_key=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    Tags=models.ManyToManyField(Tags)

    def __str__(self):
        return self.ID

class ProductInventory(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    user_alert_threshold=models.IntegerField(default=0)
    back_order_threshold=models.IntegerField(default=0)
    reorder_threshold=models.IntegerField(default=0)
    instock_count=models.IntegerField(default=0)
    reversed_count=models.IntegerField(default=0)

    def __str__(self):
        return self.product


class Productsummary(models.Model):
    product_id=models.ForeignKey(Product, on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    content=models.TextField()

    def __str__(self):
        return self.title

class Costtypes(models.Model):
    COST_CATEGORY_CHOICES = [
        ('Product', 'Product'),
        ('Nonproduct', 'Nonproduct'),
        ('Tax', 'Tax'),
        ('Discount', 'Discount'),
    ]
    Transaction_choices=[
        ('D','Debit'),
        ('C','Credit'),
    ]
    ID=models.CharField(max_length=255,primary_key=True)
    name=models.CharField(max_length=255)
    cost_category=models.CharField(choices=COST_CATEGORY_CHOICES,max_length=255)#model
    is_order_level_cost=models.BooleanField()
    is_order_item_level_cost=models.BooleanField()
    transaction_type=models.CharField(choices=Transaction_choices,max_length=255)

    def __str__(self):
        return self.name

class orders(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('InProgress', 'InProgress'),
        ('Completed', 'Completed'),
    ]
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orderedby=models.ForeignKey(User, on_delete=models.CASCADE)
    orderedon=models.DateTimeField(auto_now_add=True)
    orderstatus=models.CharField(choices=STATUS_CHOICES,max_length=255)#model

    def __str__(self):
        return self.ID

class orderitems(models.Model):
    order=models.ForeignKey(orders, on_delete=models.CASCADE)
    ID=models.IntegerField(primary_key=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return self.ID

class orderitemcost(models.Model):
    orderitem=models.ForeignKey(orderitems, on_delete=models.CASCADE)
    cost_type=models.ForeignKey(Costtypes, on_delete=models.CASCADE,limit_choices_to={'is_order_item_level_cost': True})
    amount=models.IntegerField(default=0)
    currency_code=models.CharField(max_length=255)#model

    def __str__(self):
        return f'{self.orderitem}'

class ordercosts(models.Model):
    order=models.ForeignKey(orders, on_delete=models.CASCADE)
    cost_type = models.ForeignKey(Costtypes, on_delete=models.CASCADE,limit_choices_to={'is_order_item_level_cost': True})
    amount = models.IntegerField(default=0)
    currency_code = models.CharField(max_length=255)#model

    def __str__(self):
        return f'{self.order}'



# class Attribute_Tab(models.Model):
#     ID=models.CharField(max_length=255,primary_key=True)
#     tabcode=models.CharField(max_length=255)
#     name=models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.tabcode
#
# class Attribute_Section(models.Model):
#     ID=models.CharField(max_length=255,primary_key=True)
#     tab=models.ForeignKey(Attribute_Tab, on_delete=models.CASCADE)
#     sectioncode=models.CharField(max_length=255)
#     name=models.CharField(max_length=255)
#
#     def __str__(self):
#         return self.sectioncode

class Choice(models.Model):
    ID=models.CharField(max_length=255,primary_key=True)
    group_name=models.CharField(max_length=255)

    def __str__(self):
        return self.group_name

class Choice_name(models.Model):
    ID=models.CharField(max_length=255,primary_key=True)
    choice_name=models.CharField(max_length=255)

    def __str__(self):
        return self.choice_name

class Choice_group(models.Model):
    ID=models.CharField(max_length=255,primary_key=True)
    group_name=models.ForeignKey(Choice, on_delete=models.CASCADE)
    choice_name=models.ManyToManyField(Choice_name)

    def __str__(self):
        return f'{self.group_name} - {self.choice_name}'

    @staticmethod
    def already_exists(group_name):
        return Choice_group.objects.filter(group_name=group_name).exists()

class Attribute(models.Model):
    DATATYPE_CHOICES = [
        ('Text', 'Text'),
        ('Number', 'Number'),
        ('Date', 'Date'),
        ('Time', 'Time'),
        ('single_choice', 'Single Choice'),
        ('multi_choice', 'Multi Choice'),
    ]

    ID=models.CharField(max_length=255,primary_key=True)
    attributecode=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    datatype=models.CharField(choices=DATATYPE_CHOICES,max_length=255)
    min_value=models.IntegerField(blank=True)
    max_value=models.IntegerField(blank=True)
    dataformat=models.DateField(blank=True)
    timeformat=models.TimeField(blank=True)

    def clean(self):
        # Date and time format lists
        date_formats = [
            '%Y', '%y', '%m%Y', '%m%y', '%b%Y', '%b%y', '%d%m%y', '%d%m%Y'
        ]
        time_formats = [
            '%H:%M', '%H:%M:%S'
        ]

        if self.timeformat:
            self.timeformat = self._validate_format(self.timeformat, time_formats, 'time')

        # Validate date format
        if self.dataformat:
            self.dataformat = self._validate_format(self.dataformat, date_formats, 'date')

    def _validate_format(self, value, formats, field_type):

        for fmt in formats:
            try:
                if field_type == 'date':
                    return datetime.strptime(str(value), fmt).date()
                elif field_type == 'time':
                    return datetime.strptime(str(value), fmt).time()
            except (ValueError, TypeError):
                continue
        raise ValidationError(f"Invalid {field_type} format: {value}. Please use a valid format.")

class ProductAttribute(models.Model):
    product_attribute_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    productcode = models.ForeignKey(Product, on_delete=models.CASCADE)
    attributecode = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    tabcode = models.CharField(max_length=10)
    sectioncode = models.CharField(max_length=10, null=True, blank=True)


    def __str__(self):
        return self.productcode

class ProductAttributeValue(models.Model):
    product_attribute_id=models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value=models.CharField(max_length=255)
    choice_value=models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return self.value


#####JSON
# class Attribute(djongo_models.Model):
#     Attributecode = models.CharField(max_length=10)
#     class Meta:
#         abstract = True
# #
# class Section(djongo_models.Model):
#     Sectioncode = models.CharField(max_length=10, null=True, blank=True)
#     Attributes = models.ArrayField(model_container=Attribute)
#     class Meta:
#         abstract = True
#
# class Tab(djongo_models.Model):
#     Tabcode = models.CharField(max_length=10)
#     Sections = models.ArrayField(model_container=Section)
#     class Meta:
#         abstract = True
#
# class Product(djongo_models.Model):
#     Productcode = models.CharField(max_length=10)
#     Tabs = models.ArrayField(model_container=Tab)




