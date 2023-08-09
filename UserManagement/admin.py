from django.contrib import admin
from .models import SolutionUser
from django.contrib.auth.admin import UserAdmin
from .forms import *
# Register your models here.

class SolutionUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = SolutionUser
    #Note: Remove Password and Key
    list_display = ['is_staff', 'username', 'email', 'password', 'key', 'is_active']

# Registrations
admin.site.register(SolutionUser, SolutionUserAdmin)

#uncomment when user profile system is useable
##admin.site.register(SolutionUserProfile, SolutionUserAdmin)