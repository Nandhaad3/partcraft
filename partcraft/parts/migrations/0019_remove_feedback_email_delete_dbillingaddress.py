# Generated by Django 4.1.13 on 2024-09-16 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parts', '0018_alter_feedback_email_delete_dbillingaddress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='email',
        ),
    ]