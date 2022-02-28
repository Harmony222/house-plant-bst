# Generated by Django 4.0.1 on 2022-02-28 18:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('plant', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=150)),
                ('city', models.CharField(max_length=150)),
                ('state', models.CharField(max_length=2)),
                ('zip', models.CharField(max_length=10)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_user_addresses', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('in_progress_date', models.DateTimeField(blank=True, null=True)),
                ('fulfilled_date', models.DateTimeField(blank=True, null=True)),
                ('canceled_date', models.DateTimeField(blank=True, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('status', models.CharField(choices=[('CR', 'Created'), ('IN', 'In-progress'), ('FU', 'Fulfilled'), ('CA', 'Canceled')], default='CR', max_length=2)),
                ('handling', models.CharField(choices=[('SH', 'Shipping'), ('PI', 'Pickup')], default='SH', max_length=2)),
                ('address_for_pickup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='get_order_pickup_address', to='order.address', verbose_name='Pickup address')),
                ('address_for_shipping', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='get_order_shipping_address', to='order.address', verbose_name='Ship to address')),
                ('buyer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_buyer_orders', to=settings.AUTH_USER_MODEL, verbose_name='Buyer')),
                ('canceled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Canceled by user')),
                ('seller', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_seller_orders', to=settings.AUTH_USER_MODEL, verbose_name='Seller')),
            ],
            options={
                'verbose_name_plural': 'Orders',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_order_items', to='order.order', verbose_name='Order')),
                ('user_plant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='get_order_items', to='plant.userplant', verbose_name='User Plant')),
            ],
            options={
                'verbose_name_plural': 'Order Items',
            },
        ),
    ]
