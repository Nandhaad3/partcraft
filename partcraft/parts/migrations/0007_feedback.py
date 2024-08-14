# Generated by Django 4.1.13 on 2024-08-14 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0006_merge_20240814_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('company_name', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('image', models.URLField()),
                ('feedback', models.CharField(max_length=255)),
            ],
        ),
    ]
