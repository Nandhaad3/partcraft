# Generated by Django 4.1.13 on 2024-09-16 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0014_rename_gst_number_billingaddress_tin_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='use_the_billing_address',
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='use_the_billing_address',
            field=models.BooleanField(default=False),
        ),
    ]