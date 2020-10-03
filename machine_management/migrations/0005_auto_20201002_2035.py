# Generated by Django 2.2.4 on 2020-10-03 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machine_management', '0004_usage_file_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usage',
            name='file_id',
        ),
        migrations.AlterField(
            model_name='tooltemperature',
            name='machine',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='machine_management.Machine'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usage',
            name='userprofile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_management.UserProfile'),
        ),
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
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.Machine')),
                ('usage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='machine_management.Usage')),
            ],
        ),
        migrations.AddField(
            model_name='machine',
            name='current_print_information',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_machine', to='machine_management.JobInformation'),
        ),
        migrations.AddField(
            model_name='tooltemperature',
            name='job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='machine_management.JobInformation'),
        ),
        migrations.AddField(
            model_name='usage',
            name='current_print_information',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job', to='machine_management.JobInformation'),
        ),
    ]
