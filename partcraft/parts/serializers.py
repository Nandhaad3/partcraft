from rest_framework import serializers
from .models import *

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

    class Meta:
        model = Product
        fields = ['id','url','parts_name', 'parts_voltage','subcategory_name',
                  'parts_litre', 'parts_type', 'parts_description', 'parts_no', 'parts_price', 'parts_offer','final_price',
                  'parts_status', 'parts_condition', 'parts_warranty', 'parts_specification',
                  'main_image','images','parts_brand', 'parts_category','this_parts_fits','wishlist','is_in_wishlist','related_products']
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
        ).exclude(id=obj.id)[:4]  # Fetch 4 related products, excluding the current one
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
    url = serializers.HyperlinkedIdentityField(view_name='getoneproduct')
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

    class Meta:
        model = Product
        fields = ['id', 'parts_name', 'parts_price', 'parts_offer', 'final_price', 'main_image', 'url']

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

