# Generated by Django 5.0.6 on 2024-06-05 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_image',
            field=models.ImageField(blank=True, upload_to='categories/'),
        ),
    ]
