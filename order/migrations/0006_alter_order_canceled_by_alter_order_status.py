# Generated by Django 4.0.1 on 2022-02-23 17:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0005_order_canceled_by_order_canceled_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='canceled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Canceled by user'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CR', 'Created'), ('IN', 'In-progress'), ('SH', 'Shipped'), ('CO', 'Complete'), ('CA', 'Canceled')], default='CR', max_length=2),
        ),
    ]