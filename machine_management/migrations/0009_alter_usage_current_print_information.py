# Generated by Django 3.2.10 on 2021-12-12 22:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0002_alter_jobinformation_id'),
        ('machine_management', '0008_auto_20210922_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usage',
            name='current_print_information',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job', to='data_management.jobinformation'),
        ),
    ]
