# Generated by Django 2.2.14 on 2020-08-25 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('season', models.CharField(max_length=255)),
                ('current', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='usage',
            name='semester',
            field=models.ForeignKey(default=1, on_delete=models.SET(None), to='machine_management.Semester'),
            preserve_default=False,
        ),
    ]