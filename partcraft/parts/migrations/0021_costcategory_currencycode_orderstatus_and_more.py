# Generated by Django 4.1.13 on 2024-09-17 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0020_alter_feedback_image_delete_dbillingaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_category', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_status', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='costtypes',
            name='cost_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.costcategory'),
        ),
        migrations.AlterField(
            model_name='ordercosts',
            name='currency_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.currencycode'),
        ),
        migrations.AlterField(
            model_name='orderitemcost',
            name='currency_code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.currencycode'),
        ),
        migrations.AlterField(
            model_name='orders',
            name='orderstatus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.orderstatus'),
        ),
        migrations.AlterField(
            model_name='product_cost',
            name='product_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parts.currencycode'),
        ),
    ]