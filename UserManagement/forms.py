from django.contrib.auth import forms as auth_forms
from .models import SolutionUser
from django.forms import ModelForm

class UserCreationForm(ModelForm):

    class Meta:
        model = SolutionUser
        fields = ["username", "email",]
        
class UserChangeForm(auth_forms.UserChangeForm):
    class Meta:
        model = SolutionUser
        fields = ["username", "password",]
        
class AccountDeleteForm(ModelForm):
    class Meta:
        model = SolutionUser
        fields = ['is_active']
        
class PasswordChangeForm(auth_forms.SetPasswordForm):
    
    class Meta:
        model = SolutionUser