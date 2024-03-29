# Generated by Django 2.2.14 on 2020-11-15 07:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_management', '__first__'),
        ('business','0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.CharField(max_length=255, unique=True)),
                ('in_use', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True)),
                ('status_message', models.CharField(blank=True, default='', max_length=255)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MachineSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot_name', models.CharField(max_length=255)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MachineType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_type_name', models.CharField(max_length=255, unique=True)),
                ('machine_category', models.CharField(max_length=255, null=True)),
                ('usage_policy', models.CharField(default='', max_length=4096)),
                ('hourly_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('data_entry_after_use', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_name', models.CharField(max_length=255, unique=True)),
                ('unit', models.CharField(max_length=255)),
                ('cost_per', models.DecimalField(decimal_places=2, max_digits=5)),
                ('in_stock', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('for_class', models.BooleanField(default=False)),
                ('is_reprint', models.BooleanField(default=False)),
                ('own_material', models.BooleanField(default=False)),
                ('cost_override', models.BooleanField(default=False)),
                ('overridden_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('cost_override_reason', models.CharField(blank=True, default='', max_length=512)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('clear_time', models.DateTimeField(blank=True, null=True)),
                ('retry_count', models.PositiveIntegerField(default=0)),
                ('status_message', models.CharField(default='In Progress.', max_length=255)),
                ('complete', models.BooleanField(default=False)),
                ('error', models.BooleanField(default=False)),
                ('failed', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('semester', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.Semester')),
                ('machine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='machine_management.Machine')),
                ('userprofile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='SlotUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=5, max_digits=10)),
                ('deleted', models.BooleanField(default=False)),
                ('machine_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.MachineSlot')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.Resource')),
                ('usage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.Usage')),
            ],
        ),
        migrations.AddField(
            model_name='machineslot',
            name='allowed_resources',
            field=models.ManyToManyField(to='machine_management.Resource'),
        ),
        migrations.AddField(
            model_name='machineslot',
            name='machine_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.MachineType'),
        ),
        migrations.AddField(
            model_name='machine',
            name='current_job',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_machine', to='machine_management.Usage'),
        ),
        migrations.AddField(
            model_name='machine',
            name='machine_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machine_management.MachineType'),
        ),
    ]
