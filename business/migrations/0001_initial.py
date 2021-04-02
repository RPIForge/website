# Generated by Django 2.2.14 on 2021-04-02 19:35


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('season', models.CharField(max_length=255)),
                ('current', models.BooleanField(default=True)),
            ],
        ),
    ]
