# Generated by Django 2.2.14 on 2021-04-02 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('machine_management', '0004_auto_20201115_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('status_message', models.CharField(default='In Progress.', max_length=255)),
                ('complete', models.BooleanField(default=False)),
                ('error', models.BooleanField(default=False)),
                ('file_id', models.CharField(blank=True, default=None, max_length=36, null=True)),
                ('layer_count', models.IntegerField(blank=True, null=True)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.Machine')),
                ('usage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='machine_management.Usage')),
            ],
        ),
    ]
