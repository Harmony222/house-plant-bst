# Generated by Django 4.0.1 on 2022-02-01 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0002_alter_message_thread_delete_thread'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='thread',
            new_name='trade',
        ),
    ]