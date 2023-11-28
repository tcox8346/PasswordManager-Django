from typing import Any
from django.forms import ModelForm, CharField, Form, ValidationError
from django.contrib.auth import get_user_model
from .models import FriendRequest
    
   
def UserExists_Validatior(value):
    if type(value) != str:
        raise ValidationError("Name must be a string")
    # Check if username exists in user model
    user_record = get_user_model().objects.filter(username = value).exists()
    if not user_record:
        raise ValidationError("User Must Exists") 


        
class FriendRequestForm_CheckUsername(Form):
    """Form that Recieves a username in string format and returns valid if user exists"""
    requested_user = CharField(label='User Name',max_length=100, required=True, empty_value='', strip=True,  validators = ([UserExists_Validatior]))
   
# TODO
