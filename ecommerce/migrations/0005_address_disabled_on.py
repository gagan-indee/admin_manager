# Generated by Django 5.1 on 2024-08-27 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0004_alter_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='disabled_on',
            field=models.DateTimeField(null=True),
        ),
    ]
