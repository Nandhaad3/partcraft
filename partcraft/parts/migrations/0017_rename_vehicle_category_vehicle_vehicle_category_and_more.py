# Generated by Django 4.1.13 on 2024-09-16 11:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0016_remove_billingaddress_use_the_billing_address_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='Vehicle_category',
            new_name='vehicle_category',
        ),
    ]
