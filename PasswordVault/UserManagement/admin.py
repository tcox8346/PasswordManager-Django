from django.contrib import admin
from .models import SolutionUser, SolutionUserProfile
from django.contrib.auth.admin import UserAdmin
from .forms import UserChangeForm,UserCreationForm
# Register your models here.

class SolutionUserAdmin(UserAdmin):
    add_form:UserCreationForm = UserCreationForm
    form = UserChangeForm
    model = SolutionUser
    #Note: Remove Password and Key
    list_display = ['is_staff', 'username','password','email', 'is_active', 'slug']
    #prepopulated_fields = {"slug": ["username"]} 

class SolutionProfileAdmin(admin.ModelAdmin):
    list_filter = ['user', 'shared_key']
    list_display = ['user', 'shared_key', 'slug']
    search_fields = ['user__username']
    class Meta:
        model = SolutionUserProfile
        
    


# Registrations
admin.site.register(SolutionUser, SolutionUserAdmin)
admin.site.register(SolutionUserProfile, SolutionProfileAdmin)