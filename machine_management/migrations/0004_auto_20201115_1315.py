# Generated by Django 2.2.14 on 2020-11-15 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('machine_management', '0003_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='semester',
            name='usage_summary',
        ),
        migrations.RemoveField(
            model_name='semester',
            name='usage_update',
        ),
    ]
