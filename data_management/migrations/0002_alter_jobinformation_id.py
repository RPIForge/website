# Generated by Django 3.2.5 on 2021-07-09 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobinformation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
