# Generated by Django 4.2.2 on 2023-11-18 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CredentialVault', '0004_remove_notification_silenced_on_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='other_user',
            field=models.CharField(default=None, max_length=100, null=True, verbose_name='requesting_user'),
        ),
    ]