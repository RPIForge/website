# Generated by Django 2.2.14 on 2020-11-15 06:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('machine_management', '0002_stuff'),
    ]

    operations = [
        migrations.AddField(
            model_name='semester',
            name='usage_summary',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='semester',
            name='usage_update',
            field=models.DateField(null=True),
        ),
    ]
