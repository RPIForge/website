# Generated by Django 3.2.5 on 2021-07-19 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_alter_userprofile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='rin',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
