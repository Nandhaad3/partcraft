# Generated by Django 4.1.13 on 2024-08-05 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0003_order_productordercount'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_fit',
            field=models.CharField(blank=True, choices=[('No Guarantee fit', 'No Guarantee fit'), ('Guarantee fit', 'Guarantee fit')], max_length=255, null=True),
        ),
    ]