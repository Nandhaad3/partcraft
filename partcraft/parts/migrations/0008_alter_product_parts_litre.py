# Generated by Django 5.0.6 on 2024-06-05 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0007_alter_product_parts_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='parts_litre',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
