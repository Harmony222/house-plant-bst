# Generated by Django 4.0.1 on 2022-02-01 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plant', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plantcommonname',
            name='name',
            field=models.CharField(max_length=150, verbose_name='Common Name'),
        ),
    ]
