# Generated by Django 3.2.5 on 2021-07-19 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization_management', '0004_auto_20210719_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='password'),
        ),
    ]
