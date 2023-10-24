from typing import Any
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

#TODO Fix user form to remove the passing of password1 and 2, or pass a single value - not sure if this is because of the redirect after account creation
class AdminUsedUserCreationForm(UserCreationForm):
   
    class Meta:
        model = SolutionUser
        fields = ["username", "email",]     
    
#Form associated with passwordgeneration model
    



    
        
    
    
    
    
    