# Generated by Django 5.0.4 on 2024-05-09 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='description',
            field=models.TextField(blank=True, max_length=500),
        ),
    ]