# Generated by Django 4.2.2 on 2023-10-17 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordGeneration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dictionaryCore', models.CharField(blank=True, default='', max_length=500, null=True)),
                ('dictionaryRelated', models.CharField(blank=True, default='', max_length=1500, null=True)),
                ('minimum_words', models.IntegerField(default=3)),
                ('minimum_numbers', models.IntegerField(default=3)),
                ('minimum_special_characters', models.IntegerField(default=3)),
            ],
            options={
                'verbose_name': 'passwordgenerators',
                'verbose_name_plural': 'passwordgenerators',
            },
        ),
    ]
