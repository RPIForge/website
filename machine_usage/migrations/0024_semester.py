# Generated by Django 2.2.14 on 2020-08-25 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_usage', '0023_userprofile_entertainment_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('season', models.CharField(max_length=255)),
            ],
        ),
    ]
