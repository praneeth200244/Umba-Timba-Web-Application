# Generated by Django 5.0.4 on 2024-05-20 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='phone',
            new_name='phone_number',
        ),
    ]
