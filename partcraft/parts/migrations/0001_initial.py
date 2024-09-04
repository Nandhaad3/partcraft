# Generated by Django 4.2.10 on 2024-09-03 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_name', models.CharField(max_length=255)),
                ('gst_number', models.CharField(blank=True, max_length=16, null=True)),
                ('email', models.EmailField(max_length=255)),
                ('billing_address', models.CharField(max_length=1000)),
                ('contact', models.CharField(max_length=13)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50)),
                ('brand_image', models.URLField()),
            ],
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
        ),
        migrations.CreateModel(
            name='DealerAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('gst_number', models.CharField(blank=True, max_length=16, null=True)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
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
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_name', models.CharField(max_length=50)),
                ('vehicle_model', models.CharField(max_length=50)),
                ('vehicle_year', models.IntegerField()),
                ('vehicle_variant', models.CharField(choices=[('petrol', 'petrol'), ('diesel', 'diesel')], max_length=50)),
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
                ('retated_type', models.CharField(max_length=255)),
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
            name='ProductOrderCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_count', models.IntegerField(default=0)),
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
        migrations.AddField(
            model_name='product',
            name='this_parts_fits',
            field=models.ManyToManyField(to='parts.vehicle'),
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
    ]
