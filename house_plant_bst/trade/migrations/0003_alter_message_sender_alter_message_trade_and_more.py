# Generated by Django 4.0.1 on 2022-01-27 07:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plant', '0007_alter_plantcommonname_plant_alter_userplant_plant_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trade', '0002_message_sender_trade_buyer_trade_seller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='get_user_messages', to=settings.AUTH_USER_MODEL, verbose_name='Message Sender'),
        ),
        migrations.AlterField(
            model_name='message',
            name='trade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_trade_messages', to='trade.trade', verbose_name='Trade'),
        ),
        migrations.AlterField(
            model_name='tradeitem',
            name='trade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_trade_items', to='trade.trade', verbose_name='Trade'),
        ),
        migrations.AlterField(
            model_name='tradeitem',
            name='user_plant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='get_trade_items', to='plant.userplant', verbose_name='User Plant'),
        ),
    ]
