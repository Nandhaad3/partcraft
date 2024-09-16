from django.contrib import admin
from .models.models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'parts_brand','parts_category','subcategory_name','parts_price', 'parts_status','parts_offer','main_image']
#

@admin.register(RelatedProduct)
class RelatedProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'related_product1','retated_type']
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

# admin.site.register(Product)
@admin.register(Application_type)
class ApplicationTypeAdmin(admin.ModelAdmin):
    list_display = ['type_name']

@admin.register(Application_category)
class ApplicationCategoryAdmin(admin.ModelAdmin):
    list_display = ['type_name','category_name']

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_variant']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['brand_manufacturer']



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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id','name','company_name','designation','email','feedback']


# @admin.register(DealerAddress)
# class DealerAddressAdmin(admin.ModelAdmin):
#     list_display = ['name']

@admin.register(SellerGroup)
class SellerGroupAdmin(admin.ModelAdmin):
    list_display = ['group']

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller_type']


@admin.register(Product_cost)
class ProductcostAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'product_cost', 'product_currency']

@admin.register(Product_btc_partners)
class ProductbtcpartnersAdmin(admin.ModelAdmin):
    list_display = ['partner_name', 'partner_logo']

@admin.register(Product_btc_links)
class ProductbtclinksAdmin(admin.ModelAdmin):
    list_display = ['product', 'bzc_partner', 'url']

@admin.register(MerchandisingSlot)
class MerchandisingSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'Aspect_ratio_threshold']

@admin.register(MerchandisingContent)
class MerchandisingContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'slot', 'image_url']

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ['ID', 'tag_name', 'is_active']


@admin.register(ProductTags)
class ProductTagsAdmin(admin.ModelAdmin):
    list_display = ['ID']


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'user_alert_threshold', 'back_order_threshold']

@admin.register(Productsummary)
class ProductsummaryAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'title', 'content']

@admin.register(Costtypes)
class CosttypesAdmin(admin.ModelAdmin):
    list_display = ['ID', 'name', 'cost_category']

@admin.register(orders)
class ordersAdmin(admin.ModelAdmin):
    list_display = ['ID', 'orderedby', 'orderedon']

@admin.register(orderitems)
class orderitemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'ID', 'product']

@admin.register(orderitemcost)
class orderitemcostAdmin(admin.ModelAdmin):
    list_display = ['orderitem', 'cost_type', 'amount']

@admin.register(ordercosts)
class ordercostsAdmin(admin.ModelAdmin):
    list_display = ['order', 'cost_type', 'amount']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['ID', 'group_name']

@admin.register(Choice_name)
class ChoicenameAdmin(admin.ModelAdmin):
    list_display = ['ID', 'choice_name']

@admin.register(Choice_group)
class ChoicegroupAdmin(admin.ModelAdmin):
    list_display = ['ID', 'group_name']

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['ID', 'attributecode', 'name']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['product_attribute_id', 'productcode', 'attributecode']

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['product_attribute_id', 'value', 'choice_value']



