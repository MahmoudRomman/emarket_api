# Generated by Django 5.1.5 on 2025-02-22 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_rename_product_item_rename_product_review_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='stock',
            new_name='quantity',
        ),
    ]
