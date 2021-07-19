# Generated by Django 3.2.5 on 2021-07-19 14:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization_management', '0003_organizationmembership'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='foapal_fund',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='foapal_org',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='machine_access',
            field=models.ManyToManyField(blank=True, null=True, related_name='_organization_management_organization_machine_access_+', to='organization_management.Organization'),
        ),
        migrations.AlterField(
            model_name='organizationmembership',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL),
        ),
    ]
