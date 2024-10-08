# Generated by Django 4.1.13 on 2024-09-21 04:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parts', '0006_selectedseller'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_model', models.CharField(max_length=255)),
                ('vehicle_year', models.IntegerField()),
                ('vehicle_variant', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vehicle_make', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.manufacturer')),
            ],
        ),
    ]
