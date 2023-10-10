from typing import Any
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

class CredentialRecord(models.Model):
    # Usermanagement record that specifies the user who owns the record
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='credentials', to_field='username')
       # Service feild: This fields holds what service is tied to the credential record, i.e the service provider of the credential
    service_provider = models.CharField(blank=True,default='Undefined', max_length=50)
    username = models.CharField(blank=False, max_length=50)
    password =  models.CharField(blank=False, max_length=50, default='Uninitialized')  #This is to be in encrypted form - Derive a model class that uses a key provided by user to encrpyt and decrypt
    email = models.EmailField(blank=True, null=True, default=None) # An optional field that denotes the email address associated with the record
    Share_state = (('Public','shared'), ('Private','unshared')) # Specifier that designates if a record is shared to friend profiles
    
    # Service choices stores a value that denotes the class of record. For example
        # if the record is for business purposes, personel, or undefined.
    ## The Service type is a a way of grouping service records by purpose, it uses the choices of the above type.
    service_type = models.CharField(choices=Share_state, default= Share_state[0] ,blank=True, max_length=50)
    #Shares field: This field holds a collection of string values that designate the usernames that can access a credentials fields. This will be in csv form
        #TODO: implement model methods that return csv as list
    
    added_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    class Meta:
       constraints = [models.UniqueConstraint(fields=['service_provider', 'username', 'owner'], name="unique_service_username_owner")]
        
    def get_absolute_url(self):
        return reverse("credential_detail", kwargs={"user": self.owner.user.get_username() ,"pk": self.pk})
    def __str__(self):
        return f'credential record: {self.pk}'
    

    def share_encrpytion(self):
        if self.Share_state == 'shared':
            #if record is marked to be shared encrpyt using share key in current users profile
            pass
        pass
    
    def share_decrypt(self, friend_name):
        if self.Share_state == 'shared':
            #if record is marked to be shared decrypt using share key of friend in stored keys dictionary in current users profile
      
            pass
        pass
# Purpose: 
    # Credentials are records of information that detail a the information associated with a service account. 
        # Credential impertantent information is to be stored in encrypted forms and decrypted by a key provided to a user upon the initial creation of master account.