# Generated by Django 4.1.13 on 2024-09-19 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0003_usercoupon_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='code',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
