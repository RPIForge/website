# Generated by Django 2.2.4 on 2020-10-14 03:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machine_management', '0007_auto_20201003_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tooltemperature',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='machine_management.JobInformation'),
        ),
    ]
