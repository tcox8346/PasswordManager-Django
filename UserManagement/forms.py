from typing import Any
from django.contrib.auth import forms as auth_forms
from .models import SolutionUser, FriendRequest
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
        
#Form associated with passwordgeneration model
    
# TODO
class FriendRequestSubmissionForm(ModelForm):
    """This form is called by a valid FriendRequestForm view"""
    
    
    class Meta:
        db_table = 'FriendRequest'
        managed = True
        verbose_name = 'FriendRequest'
        verbose_name_plural = 'FriendRequests'
        model = FriendRequest
        fields = ["request_target"]
    
        error_messages = {
            "request_target": {
                "label": ("Request this user to be a friend"),
                "max_length": ("The recipient name is too long. It must be within 255 characters in length"),

            },
            
        }
        
    def clean(self):
        super().clean()
        recipient_exists = SolutionUser.objects.filter(self.cleaned_data["request_target"]).exists()
        if not recipient_exists:
            #raise validation error - User Doesnt Exists
            pass
        return 
        

    
        
    
    
    
    
    