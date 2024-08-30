# Generated by Django 5.1 on 2024-08-27 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('active', 'active'), ('completed', 'completed'), ('canceled', 'canceled')], max_length=10, null=True),
        ),
    ]