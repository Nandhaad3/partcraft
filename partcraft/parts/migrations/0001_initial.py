# Generated by Django 5.0.6 on 2024-06-05 07:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50)),
                ('brand_image', models.ImageField(upload_to='brands/')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50)),
                ('category_image', models.ImageField(upload_to='categories/')),
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
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subcategory_name', models.CharField(max_length=255)),
                ('parts_voltage', models.IntegerField()),
                ('parts_fits', models.CharField(max_length=255)),
                ('parts_litre', models.IntegerField()),
                ('parts_type', models.CharField(choices=[('OE', 'OE'), ('AFTERMARKET', 'AFTERMARKET')], max_length=255)),
                ('parts_description', models.TextField()),
                ('parts_no', models.IntegerField()),
                ('parts_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('parts_offer', models.DecimalField(decimal_places=2, max_digits=10)),
                ('parts_status', models.CharField(choices=[('in stock', 'in stock'), ('out of stock', 'out of stock')], max_length=255)),
                ('parts_conditions', models.CharField(choices=[('New', 'New'), ('Refurbished', 'Refurbished')], max_length=255)),
                ('parts_warrenty', models.DecimalField(decimal_places=2, max_digits=10)),
                ('parts_specification', models.TextField()),
                ('main_image', models.ImageField(upload_to='products/')),
                ('parts_brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.brand')),
                ('parts_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.category')),
                ('this_parts_fits', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='parts.product')),
            ],
        ),
    ]
