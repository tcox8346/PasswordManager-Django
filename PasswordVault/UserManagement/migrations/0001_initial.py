# Generated by Django 4.2.2 on 2023-10-24 02:01

import UserManagement.models
import autoslug.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolutionUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('username', models.CharField(max_length=255, null=True, unique=True)),
                ('email', models.EmailField(default='', max_length=254)),
                ('password', models.CharField(max_length=1024, null=True)),
                ('key', models.CharField(max_length=128, null=True, unique=True)),
                ('is_new', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('slug', autoslug.fields.AutoSlugField(default='', editable=False, populate_from='username', unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', UserManagement.models.SolutionUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tokenValue', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('activeState', models.IntegerField(blank=True, default=0)),
                ('activeTimeFrame', models.DurationField(default=datetime.timedelta(seconds=36000), null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='TokenOwner')),
            ],
        ),
        migrations.CreateModel(
            name='SolutionUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, height_field=20, upload_to=None, width_field=20)),
                ('shared_key', models.CharField(blank=True, default='', max_length=256)),
                ('shared_keys', models.TextField(default='')),
                ('slug', models.SlugField(default='', unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]