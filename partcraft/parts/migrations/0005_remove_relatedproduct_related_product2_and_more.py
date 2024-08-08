# Generated by Django 4.1.13 on 2024-08-07 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0004_relatedproduct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relatedproduct',
            name='related_product2',
        ),
        migrations.AddField(
            model_name='relatedproduct',
            name='related_product2',
            field=models.ManyToManyField(related_name='related_product2_set', to='parts.product'),
        ),
    ]
