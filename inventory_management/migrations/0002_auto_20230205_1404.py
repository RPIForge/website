# Generated by Django 3.2.17 on 2023-02-05 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcecategory',
            name='cost_per',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='resourcecategory',
            name='unit',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]