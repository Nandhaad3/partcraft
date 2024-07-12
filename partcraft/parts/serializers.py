from rest_framework import serializers
from .models import *
import random

class BrandSerializer(serializers.ModelSerializer):
    url=serializers.HyperlinkedIdentityField(view_name='brandonedetails')
    class Meta:
        model = Brand
        fields = ['brand_name','brand_image','url']

class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='onecategorydetails')
    class Meta:
        model = Category
        fields = ['category_name','url']

class VehicleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vehicleonedetail')
    class Meta:
        model = Vehicle
        fields = ['vehicle_name','vehicle_model','vehicle_year','vehicle_type','url']

class VehicleoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['vehicle_name','vehicle_model','vehicle_year','vehicle_type']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class WishlistSerializer(serializers.Serializer):
    class Meta:
        model = Wishlist
        fields = ['wishlist_name','wishlist_product']
        read_only_fields = ['wishlist_name']

    def create(self, validated_data):
        return Wishlist.objects.create(**validated_data)



class OfferSerializer(serializers.ModelSerializer):
    parts_name = serializers.SerializerMethodField()
    def arrangename(self,obj):
        return (f"{obj.parts_brand.brand_name} "
                f"{obj.parts_category.category_name} "
                f"{obj.subcategory_name} "
                f"{obj.parts_voltage}V "
                f"{obj.parts_fits} "
                f"{obj.parts_litre}L")
    def get_parts_name(self, obj):
        b=self.arrangename(obj)
        return b.replace('NoneL','').strip()
    url = serializers.HyperlinkedIdentityField(view_name='offerproduct')
    class Meta:
        model = Product
        fields = ['parts_name','parts_offer','url']

class ProductSerializer(serializers.ModelSerializer):
    parts_brand = BrandSerializer()
    parts_category = CategorySerializer()
    this_parts_fits = VehicleSerializer(many=True)
    images = ProductImageSerializer(many=True)
    parts_name = serializers.SerializerMethodField()
    final_price=serializers.SerializerMethodField()
    url=serializers.HyperlinkedIdentityField(view_name='getoneproduct')
    wishlist=serializers.HyperlinkedIdentityField(view_name='wishlistcreate')
    is_in_wishlist = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()
    similar_products = serializers.SerializerMethodField()
    addtocart= serializers.HyperlinkedIdentityField(view_name='Cartlistcreate')
    buynow = serializers.HyperlinkedIdentityField(view_name='buy_now')

    class Meta:
        model = Product
        fields = ['id','url','parts_name', 'parts_voltage','subcategory_name',
                  'parts_litre', 'parts_type', 'parts_description', 'parts_no', 'parts_price', 'parts_offer','final_price',
                  'parts_status', 'parts_condition', 'parts_warranty', 'parts_specification',
                  'main_image','images','parts_brand', 'parts_category','this_parts_fits','wishlist','is_in_wishlist','related_products','similar_products','addtocart', 'buynow']
    def arrangename(self,obj):
        return (f"{obj.parts_brand.brand_name} "
                f"{obj.parts_category.category_name} "
                f"{obj.subcategory_name} "
                f"{obj.parts_voltage}V "
                f"{obj.parts_fits} "
                f"{obj.parts_litre}L")
    def get_parts_name(self, obj):
        b=self.arrangename(obj)
        return b.replace('NoneL','').strip()


    def get_final_price(self, obj):
        discount_amount = obj.parts_price * (obj.parts_offer / 100)
        final_price = obj.parts_price - discount_amount
        return final_price

    def get_related_products(self, obj):
        related_products = Product.objects.filter(
            parts_category=obj.parts_category
        ).exclude(subcategory_name=obj.subcategory_name)  # Fetch 4 related products, excluding the current one
        print(related_products)
        related_products_list = list(related_products)
        sample_size = min(4, len(related_products_list))
        random_related_products = random.sample(related_products_list, sample_size)
        serializer = ProductoneSerializer(random_related_products, many=True, context=self.context)
        return serializer.data
    def get_similar_products(self, obj):
        print(obj.subcategory_name)
        related_products = Product.objects.filter(
            subcategory_name=obj.subcategory_name
        ).exclude(id=obj.id)  # Fetch 4 related products, excluding the current one
        print(related_products)
        serializer = ProductoneSerializer(related_products, many=True, context=self.context)
        return serializer.data
    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)
        if not request.user.is_authenticated:
            return 'SIGN IN REQUEST'
        elif request is None:
            return False
        return Wishlist.objects.filter(wishlist_name=request.user.id,wishlist_product=obj).exists()
    def create(self, validated_data):
        brand_data = validated_data.pop('parts_brand')
        category_data = validated_data.pop('parts_category')
        vehicle_data = validated_data.pop('this_parts_fits')
        images_data = validated_data.pop('images', [])

        brand, created = Brand.objects.get_or_create(**brand_data)
        category, created = Category.objects.get_or_create(**category_data)
        vehicle, created = Vehicle.objects.get_or_create(**vehicle_data)

        product = Product.objects.create(parts_brand=brand, parts_category=category, this_parts_fits=vehicle, **validated_data)

        for vehicle in vehicle_data:
            vehicle_obj, created = Vehicle.objects.get_or_create(**vehicle)
            product.this_parts_fits.add(vehicle_obj)

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product

    def update(self, instance, validated_data):
        brand_data = validated_data.pop('parts_brand')
        category_data = validated_data.pop('parts_category')
        vehicle_data = validated_data.pop('this_parts_fits')
        images_data = validated_data.pop('images', [])

        instance.parts_brand.name = brand_data.get('name', instance.parts_brand.name)
        instance.parts_brand.save()

        instance.parts_category.name = category_data.get('name', instance.parts_category.name)
        instance.parts_category.save()

        instance.this_parts_fits.clear()
        for vehicle in vehicle_data:
            vehicle_obj, created = Vehicle.objects.get_or_create(**vehicle)
            instance.this_parts_fits.add(vehicle_obj)

        instance.subcategory_name = validated_data.get('subcategory_name', instance.subcategory_name)
        instance.parts_voltage = validated_data.get('parts_voltage', instance.parts_voltage)
        instance.parts_fits = validated_data.get('parts_fits', instance.parts_fits)
        instance.parts_litre = validated_data.get('parts_litre', instance.parts_litre)
        instance.parts_type = validated_data.get('parts_type', instance.parts_type)
        instance.parts_description = validated_data.get('parts_description', instance.parts_description)
        instance.parts_no = validated_data.get('parts_no', instance.parts_no)
        instance.parts_price = validated_data.get('parts_price', instance.parts_price)
        instance.parts_offer = validated_data.get('parts_offer', instance.parts_offer)
        instance.parts_status = validated_data.get('parts_status', instance.parts_status)
        instance.parts_condition = validated_data.get('parts_condition', instance.parts_condition)
        instance.parts_warranty = validated_data.get('parts_warranty', instance.parts_warranty)
        instance.parts_specification = validated_data.get('parts_specification', instance.parts_specification)
        instance.main_image = validated_data.get('main_image', instance.main_image)
        instance.save()

        # Update images
        keep_images = []
        for image_data in images_data:
            image_id = image_data.get('id')
            if image_id:

                image_instance = ProductImage.objects.get(id=image_id, product=instance)
                image_instance.image = image_data.get('image', image_instance.image)
                image_instance.save()
                keep_images.append(image_instance.id)
            else:

                new_image = ProductImage.objects.create(product=instance, **image_data)
                keep_images.append(new_image.id)


        for image_instance in instance.images.all():
            if image_instance.id not in keep_images:
                image_instance.delete()

        return instance

class ProductoneSerializer(serializers.ModelSerializer):
    parts_name = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    product_full_detail = serializers.HyperlinkedIdentityField(view_name='getoneproduct')
    wishlist = serializers.HyperlinkedIdentityField(view_name='wishlistcreate')
    is_in_wishlist = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ['id','parts_type' ,'parts_name', 'parts_price', 'parts_offer', 'final_price', 'main_image', 'product_full_detail','wishlist','is_in_wishlist']

    def arrangename(self,obj):
        return (f"{obj.parts_brand.brand_name} "
                f"{obj.parts_category.category_name} "
                f"{obj.subcategory_name} "
                f"{obj.parts_voltage}V "
                f"{obj.parts_fits} "
                f"{obj.parts_litre}L")
    def get_parts_name(self, obj):
        b=self.arrangename(obj)
        return b.replace('NoneL','').strip()
    def get_final_price(self, obj):
        discount_amount = obj.parts_price * (obj.parts_offer / 100)
        final_price = obj.parts_price - discount_amount
        return final_price

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)
        if not request.user.is_authenticated:
            return 'SIGN IN REQUEST'
        elif request is None:
            return False
        return Wishlist.objects.filter(wishlist_name=request.user.id, wishlist_product=obj).exists()

class WishallSerializer(serializers.ModelSerializer):
    wishlist_product=ProductSerializer()
    wishlist_name = serializers.SerializerMethodField()
    wishlist_delete=serializers.HyperlinkedIdentityField(view_name='wishdeleteoneitem')
    # wishlistdelall=serializers.HyperlinkedIdentityField(view_name='wishdeleteitem')
    class Meta:
        model = Wishlist
        fields = ['wishlist_name','wishlist_product','wishlist_delete']
        read_only_fields = ['wishlist_name']

    def arrangename(self,obj):
        return (f"{obj.parts_brand.brand_name} "
                f"{obj.parts_category.category_name} "
                f"{obj.subcategory_name} "
                f"{obj.parts_voltage}V "
                f"{obj.parts_fits} "
                f"{obj.parts_litre}L")
    def get_parts_name(self, obj):
        b=self.arrangename(obj)
        return b.replace('NoneL','').strip()
    def get_wishlist_name(self, obj):
        return obj.wishlist_name.email

class CartSerializer(serializers.ModelSerializer):
    user_name=serializers.SerializerMethodField()
    parts_name = serializers.SerializerMethodField()
    parts_offer = serializers.SerializerMethodField()
    parts_price = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    main_image=serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['user','user_name','session_key','product','quantity','parts_name','parts_price','parts_offer','discount_amount','final_price','main_image']

    def get_user_name(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.user.email
        else:
            return None
    def arrangename(self,product):
        return (f"{product.parts_brand.brand_name} "
                f"{product.parts_category.category_name} "
                f"{product.subcategory_name} "
                f"{product.parts_voltage}V "
                f"{product.parts_fits} "
                f"{product.parts_litre}L")

    def get_parts_name(self, obj):
        product=obj.product
        b=self.arrangename(product)
        return b.replace('NoneL','').strip()

    def get_parts_offer(self,obj):
        product=obj.product
        return product.parts_offer
    def get_parts_price(self,obj):
        product=obj.product
        return product.parts_price
    def get_discount_amount(self,obj):
        product=obj.product
        discount_amount = product.parts_price * (product.parts_offer / 100)
        return discount_amount


    def get_final_price(self, obj):
        product=obj.product
        print(product.parts_price,product.parts_offer)
        discount_amount = product.parts_price * (product.parts_offer / 100)
        final_amount=product.parts_price - discount_amount
        return final_amount

    def get_main_image(self,obj):
        product=obj.product
        return product.main_image
    def create(self, validated_data):
        request=self.context.get('request')
        if request.user.is_authenticated:
            validated_data['user']=request.user
        else:
            validated_data['session_key']=request.session.session_key
        return Cart.objects.create(**validated_data)


class Carouselserilizers(serializers.ModelSerializer):
    discount=serializers.SerializerMethodField()
    ref=serializers.SerializerMethodField()
    brand=serializers.SerializerMethodField()
    image=serializers.SerializerMethodField()
    code=serializers.SerializerMethodField()
    category=serializers.SerializerMethodField()
    url=serializers.HyperlinkedIdentityField(view_name='carouseloneview')


    class Meta:
        model=Carousel
        fields = ['image','discount','category','code','ref','brand','url']


    def get_code(self,obj):
        return obj.carousel_code

    def get_category(self,obj):
        return obj.carousel_category.category_name

    def get_image(self,obj):
        return obj.carousel_image
    def get_discount(self,obj):
        return f'Get {obj.carousel_offer}% off'
    def get_ref(self,obj):
        return f'{obj.carousel_offer}% off {obj.carousel_category.category_name}'
    def get_brand(self,obj):
        return f'{obj.carousel_brand.brand_name} brand only'

class Billaddressserializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = '__all__'

class Shippingaddressserializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class Buynowserilizers(serializers.Serializer):
    billing_address = Billaddressserializer()
    shipping_address = Shippingaddressserializer(required=False)
    use_same_address_for_shipping = serializers.BooleanField(default=False)
    use_the_address_for_next_time = serializers.BooleanField(default=False)

    def to_internal_value(self, data):
        return_user = self.context["request"].user
        if 'billing_address' in data:
            data['billing_address']['user'] = return_user.id
        if 'shipping_address' in data:
            data['shipping_address']['user'] = return_user.id

        return super().to_internal_value(data)

    def create(self, validated_data):
        billing_address_data = validated_data.pop('billing_address')
        use_same_address_for_shipping = validated_data.pop('use_same_address_for_shipping', False)
        use_the_address_for_next_time = validated_data.pop('use_the_address_for_next_time', False)
        user = self.context['request'].user

        # Create BillingAddress instance
        billing_address_data['user'] = user
        billing_instance = BillingAddress.objects.create(**billing_address_data)

        print(billing_instance)

        shipping_instance = None
        if use_same_address_for_shipping:
            shipping_address_data = {
                'user': user,
                'shipping_name': billing_instance.billing_name,
                'email': billing_instance.email,
                'shipping_address': billing_instance.billing_address,
                'contact': billing_instance.contact,
            }
            shipping_instance = ShippingAddress.objects.create(**shipping_address_data)
        else:
            shipping_address_data = validated_data.pop('shipping_address', None)
            if shipping_address_data:
                shipping_address_data['user'] = user
                shipping_instance = ShippingAddress.objects.create(**shipping_address_data)

        if use_the_address_for_next_time:
            user_profile, created = Profile.objects.get_or_create(user=user)
            user_profile.preferred_billing_address = billing_instance
            user_profile.preferred_shipping_address = shipping_instance
            user_profile.save()

        return {
            "billing_address": billing_instance,
            "shipping_address": shipping_instance,
        }

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'order_date']

class Bestsellingserializer(serializers.ModelSerializer):
    parts_type = serializers.SerializerMethodField(source='product.parts_type')
    parts_name = serializers.SerializerMethodField()
    parts_price = serializers.SerializerMethodField()
    parts_offer = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    product_full_detail = serializers.HyperlinkedIdentityField(view_name='getoneproduct')
    wishlist = serializers.HyperlinkedIdentityField(view_name='wishlistcreate')
    is_in_wishlist = serializers.SerializerMethodField()
    class Meta:
        model = ProductOrderCount
        fields = ['id', 'parts_type', 'parts_name', 'parts_price', 'parts_offer', 'final_price', 'main_image', 'product_full_detail', 'wishlist', 'is_in_wishlist']

    def get_parts_type(self, obj):
        return obj.product.parts_type
    def arrangename(self, obj):
        product = obj.product
        return (f"{product.parts_brand.brand_name} "
                f"{product.parts_category.category_name} "
                f"{product.subcategory_name} "
                f"{product.parts_voltage}V "
                f"{product.parts_fits} "
                f"{product.parts_litre}L")

    def get_parts_name(self, obj):
        b = self.arrangename(obj)
        return b.replace('NoneL', '').strip()

    def get_parts_price(self, obj):
        return obj.product.parts_price

    def get_parts_offer(self, obj):
        return obj.product.parts_offer

    def get_final_price(self, obj):
        product = obj.product
        discount_amount = product.parts_price * (product.parts_offer / 100)
        final_price = product.parts_price - discount_amount
        return final_price

    def get_main_image(self, obj):
        return obj.product.main_image

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)
        if not request.user.is_authenticated:
            return 'SIGN IN REQUEST'
        elif request is None:
            return False
        return Wishlist.objects.filter(wishlist_name=request.user.id, wishlist_product=obj).exists()

class Carouselpostserializer(serializers.ModelSerializer):
    # code=serializers.SerializerMethodField()

    class Meta:
        model=Carousel
        fields=['carousel_code']

    # def get_code(self,obj):
    #     return obj.carousel_code