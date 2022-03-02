# Generated by Django 4.0.1 on 2022-02-22 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_remove_order_address_order_address_for_pickup_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='handling',
            field=models.CharField(choices=[('SH', 'Shipping'), ('PI', 'Pickup')], default='SH', max_length=2),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_for_pickup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='get_order_pickup_address', to='order.address', verbose_name='Pickup address'),
        ),
        migrations.AlterField(
            model_name='order',
            name='address_for_shipping',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='get_order_shipping_address', to='order.address', verbose_name='Ship to address'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CR', 'Created'), ('IN', 'In-process'), ('SH', 'Shipped'), ('CO', 'Complete'), ('CA', 'Canceled')], default='CR', max_length=2),
        ),
    ]
