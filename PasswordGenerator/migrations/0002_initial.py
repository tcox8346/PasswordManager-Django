# Generated by Django 4.2.2 on 2023-11-07 18:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('PasswordGenerator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordgeneration',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Connected_Owner'),
        ),
    ]
