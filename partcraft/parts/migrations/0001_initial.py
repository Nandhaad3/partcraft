# Generated by Django 5.0.6 on 2024-06-11 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
    ]
