# Generated by Django 4.1.13 on 2024-09-18 00:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parts', '0026_remove_product_cost_effective_from_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='preferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selecter_seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.seller')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]