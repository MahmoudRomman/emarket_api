# Generated by Django 5.1.5 on 2025-01-18 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='slug',
        ),
    ]
