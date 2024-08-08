# Generated by Django 4.1.13 on 2024-08-07 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0003_order_productordercount'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('retated_type', models.CharField(max_length=255)),
                ('related_product1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_product1_set', to='parts.product')),
                ('related_product2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_product2_set', to='parts.product')),
            ],
        ),
    ]
