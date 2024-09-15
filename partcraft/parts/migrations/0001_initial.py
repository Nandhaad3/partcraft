# Generated by Django 4.1.13 on 2024-09-14 19:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application_category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=100, verbose_name='categories_name')),
            ],
            options={
                'verbose_name': 'Application_category',
            },
        ),
        migrations.CreateModel(
            name='Application_type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('attributecode', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('datatype', models.CharField(choices=[('Text', 'Text'), ('Number', 'Number'), ('Date', 'Date'), ('Time', 'Time'), ('single_choice', 'Single Choice'), ('multi_choice', 'Multi Choice')], max_length=255)),
                ('min_value', models.IntegerField(blank=True)),
                ('max_value', models.IntegerField(blank=True)),
                ('dataformat', models.DateField(blank=True)),
                ('timeformat', models.TimeField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_name', models.CharField(max_length=255)),
                ('gst_number', models.CharField(blank=True, max_length=16, null=True)),
                ('email', models.EmailField(max_length=255)),
                ('billing_address', models.CharField(max_length=1000)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Product Brand',
            },
        ),
        migrations.CreateModel(
            name='Carousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carousel_image', models.URLField()),
                ('carousel_offer', models.IntegerField(default=0)),
                ('carousel_code', models.CharField(max_length=255)),
                ('carousel_brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.brand')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50)),
                ('category_image', models.URLField(blank=True)),
            ],
            options={
                'verbose_name': 'Product Categories',
            },
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Costtypes',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('cost_category', models.CharField(choices=[('Product', 'Product'), ('Nonproduct', 'Nonproduct'), ('Tax', 'Tax'), ('Discount', 'Discount')], max_length=255)),
                ('is_order_level_cost', models.BooleanField()),
                ('is_order_item_level_cost', models.BooleanField()),
                ('transaction_type', models.CharField(choices=[('D', 'Debit'), ('C', 'Credit')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('company_name', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('image', models.URLField()),
                ('feedback', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('is_vehicle_manufacturer', models.BooleanField(default=False)),
                ('is_product_manufacturer', models.BooleanField(default=False)),
                ('logo', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='MerchandisingSlot',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255, unique=True)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('Aspect_ratio_threshold', models.IntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(max_length=10)),
                ('subcategory_name', models.CharField(max_length=255)),
                ('parts_voltage', models.IntegerField()),
                ('parts_fits', models.CharField(blank=True, max_length=255)),
                ('parts_litre', models.FloatField(blank=True, null=True)),
                ('parts_type', models.CharField(choices=[('OE', 'OE'), ('AFTERMARKET', 'AFTERMARKET')], max_length=255)),
                ('parts_description', models.TextField()),
                ('parts_no', models.CharField(max_length=255)),
                ('parts_price', models.IntegerField(default=0)),
                ('parts_offer', models.IntegerField()),
                ('parts_status', models.CharField(choices=[('in stock', 'in stock'), ('out of stock', 'out of stock')], max_length=255)),
                ('parts_condition', models.CharField(choices=[('New', 'New'), ('Refurbished', 'Refurbished')], max_length=255)),
                ('parts_warranty', models.IntegerField()),
                ('parts_specification', models.TextField()),
                ('main_image', models.URLField()),
                ('parts_brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.brand')),
                ('parts_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.category')),
            ],
        ),
        migrations.CreateModel(
            name='Product_btc_partners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_name', models.CharField(max_length=255)),
                ('partner_logo', models.URLField(max_length=511)),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('product_attribute_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tabcode', models.CharField(max_length=10)),
                ('sectioncode', models.CharField(blank=True, max_length=10, null=True)),
                ('attributecode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.attribute')),
                ('productcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('seller_type', models.CharField(choices=[('Manufacturer', 'Manufacturer'), ('Dealer', 'Dealer')], max_length=255)),
                ('tin', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=255)),
                ('mobile_no', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SellerGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(choices=[('City', 'City'), ('State', 'State'), ('Group of State', 'Group of State'), ('South India', 'South India'), ('North India', 'North India'), ('Other', 'Other')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('tag_name', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wishlist_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wishlist_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_model', models.CharField(max_length=500, verbose_name='model')),
                ('vehicle_year', models.IntegerField(verbose_name='year')),
                ('vehicle_variant', models.CharField(blank=True, max_length=500, verbose_name='variant')),
                ('Vehicle_category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='parts.application_category', verbose_name='Application_category')),
                ('vehicle_make', models.ForeignKey(limit_choices_to={'is_vehicle_manufacturer': True}, on_delete=django.db.models.deletion.CASCADE, to='parts.manufacturer', verbose_name='make')),
            ],
            options={
                'verbose_name': 'Application',
                'db_table': 'Application',
            },
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('shipping_address', models.CharField(max_length=1000)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('contact', models.CharField(max_length=13)),
                ('use_the_address_for_next_time', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RelatedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('retated_type', models.CharField(choices=[('similar', 'similar'), ('related', 'related')], max_length=255)),
                ('Isbidirectional', models.BooleanField()),
                ('related_product1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_product1_set', to='parts.product')),
                ('related_product2', models.ManyToManyField(related_name='related_product2_set', to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_billing_user', to='parts.billingaddress')),
                ('preferred_shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_shipping_user', to='parts.shippingaddress')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductTags',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('Tags', models.ManyToManyField(to='parts.tags')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='Productsummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductOrderCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_count', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_alert_threshold', models.IntegerField(default=0)),
                ('back_order_threshold', models.IntegerField(default=0)),
                ('reorder_threshold', models.IntegerField(default=0)),
                ('instock_count', models.IntegerField(default=0)),
                ('reversed_count', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.URLField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductAttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('choice_value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.choice')),
                ('product_attribute_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.productattribute')),
            ],
        ),
        migrations.CreateModel(
            name='Product_cost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_cost', models.IntegerField(default=0)),
                ('product_currency', models.CharField(max_length=255)),
                ('effective_from', models.DateTimeField()),
                ('cost_code', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.cost_code')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='Product_btc_links',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=511)),
                ('bzc_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product_btc_partners')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='this_parts_fits',
            field=models.ManyToManyField(to='parts.vehicle'),
        ),
        migrations.CreateModel(
            name='orders',
            fields=[
                ('ID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('orderedon', models.DateTimeField(auto_now_add=True)),
                ('orderstatus', models.CharField(choices=[('New', 'New'), ('InProgress', 'InProgress'), ('Completed', 'Completed')], max_length=255)),
                ('orderedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='orderitems',
            fields=[
                ('ID', models.IntegerField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.orders')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
            ],
        ),
        migrations.CreateModel(
            name='orderitemcost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('currency_code', models.CharField(max_length=255)),
                ('cost_type', models.ForeignKey(limit_choices_to={'is_order_item_level_cost': True}, on_delete=django.db.models.deletion.CASCADE, to='parts.costtypes')),
                ('orderitem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.orderitems')),
            ],
        ),
        migrations.CreateModel(
            name='ordercosts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('currency_code', models.CharField(max_length=255)),
                ('cost_type', models.ForeignKey(limit_choices_to={'is_order_item_level_cost': True}, on_delete=django.db.models.deletion.CASCADE, to='parts.costtypes')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.orders')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=20, unique=True)),
                ('order_date', models.DateField(auto_now_add=True)),
                ('quantity', models.IntegerField(default=1)),
                ('status', models.CharField(blank=True, choices=[('InProgress', 'InProgress'), ('Dispatched', 'Dispatched'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], max_length=255, null=True)),
                ('billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='parts.billingaddress')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
                ('shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='parts.shippingaddress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MerchandisingContent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image_url', models.URLField(blank=True, max_length=510, null=True)),
                ('click_link', models.CharField(blank=True, max_length=255, null=True)),
                ('click_link_type', models.CharField(choices=[('Internal', 'Internal'), ('External', 'External')], max_length=255)),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.merchandisingslot')),
            ],
        ),
        migrations.CreateModel(
            name='DBillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_name', models.CharField(max_length=255)),
                ('gst_number', models.CharField(blank=True, max_length=16, null=True)),
                ('email', models.EmailField(max_length=255)),
                ('billing_address', models.CharField(max_length=1000)),
                ('contact', models.CharField(blank=True, max_length=13, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Choice_name',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('choice_name', models.CharField(max_length=255)),
                ('group_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.choice')),
            ],
        ),
        migrations.CreateModel(
            name='Choice_group',
            fields=[
                ('ID', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('choice_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='parts.choice_name')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('code', models.ManyToManyField(blank=True, to='parts.carousel')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='carousel',
            name='carousel_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.category'),
        ),
        migrations.AddField(
            model_name='brand',
            name='brand_manufacturer',
            field=models.ForeignKey(limit_choices_to={'is_product_manufacturer': True}, on_delete=django.db.models.deletion.CASCADE, to='parts.manufacturer'),
        ),
        migrations.AddField(
            model_name='application_category',
            name='type_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.application_type'),
        ),
    ]
