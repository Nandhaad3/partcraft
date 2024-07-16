# Generated by Django 5.0.6 on 2024-07-02 09:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50)),
                ('brand_image', models.URLField()),
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
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_name', models.CharField(max_length=50)),
                ('vehicle_model', models.CharField(max_length=50)),
                ('vehicle_year', models.IntegerField()),
                ('vehicle_type', models.CharField(choices=[('petrol', 'petrol'), ('diesel', 'diesel')], max_length=50)),
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
                ('contact', models.CharField(max_length=13)),
                ('use_same_address_for_shipping', models.BooleanField(default=False)),
                ('use_the_address_for_next_time', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='carousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carousel_image', models.URLField()),
                ('carousel_offer', models.IntegerField(default=0)),
                ('carousel_code', models.CharField(max_length=255)),
                ('carousel_brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.brand')),
                ('carousel_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.category')),
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
                ('this_parts_fits', models.ManyToManyField(to='parts.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('code', models.ManyToManyField(blank=True, to='parts.carousel')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=255)),
                ('shipping_address', models.CharField(max_length=1000)),
                ('contact', models.CharField(max_length=13)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_billing_user', to='parts.billingaddress')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('preferred_shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_shipping_user', to='parts.shippingaddress')),
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
    ]
