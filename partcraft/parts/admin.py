from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'parts_brand','parts_category','subcategory_name','parts_price', 'parts_status','parts_offer','main_image']
#
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

# admin.site.register(Product)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_name', 'vehicle_model', 'vehicle_year', 'vehicle_type']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'brand_image']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'category_image']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['wishlist_name', 'wishlist_product']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']

@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ['carousel_image','carousel_category','carousel_code','carousel_brand']



@admin.register(BillingAddress)
class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'billing_name', 'billing_address']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'shipping_name', 'shipping_address']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_billing_address', 'preferred_shipping_address']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'order_date', 'product']

@admin.register(ProductOrderCount)
class ProductOrderCountAdmin(admin.ModelAdmin):
    list_display = ['product', 'order_count']