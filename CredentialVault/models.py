from typing import Any
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


KEY_SIZE = 256
#Custom Field



class Credentials(models.Model):
    # Usermanagement record that specifies the user who owns the record
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='credentials', to_field='username')
       # Service feild: This fields holds what service is tied to the credential record, i.e the service provider of the credential
    service = models.CharField(blank=True,default='Undefined', max_length=50)
    username = models.CharField(blank=False, max_length=50)
    password =  models.CharField(blank=False, max_length=50, default='Uninitialized')  #This is to be in encrypted form - Derive a model class that uses a key provided by user to encrpyt and decrypt
    added_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    service_choices = (('UNDEFINED','undefined'), ('BUSINESS', 'business'), ('CUSTOM','custom'))
    # Service choices stores a value that denotes the class of record. For example
        # if the record is for business purposes, personel, or undefined.
    ## The Service type is a a way of grouping service records by purpose, it uses the choices of the above type.
    service_type = models.CharField(choices=service_choices, default= service_choices[0] ,blank=True, max_length=50)
    #Shares field: This field holds a collection of string values that designate the usernames that can access a credentials fields. This will be in csv form
        #TODO: implement model methods that return csv as list
    shares = models.CharField(blank=True, max_length=10000)
    
    class Meta:
       constraints = [models.UniqueConstraint(fields=['service', 'username', 'owner'], name="unique_service_username_owner")]
        
    def get_absolute_url(self):
        return reverse("credential_detail", kwargs={"user": self.owner.get_username() ,"pk": self.pk})
    def __str__(self):
        return f'credential record: {self.pk}'
    
 
    
    

    
# Purpose: 
    # Credentials are records of information that detail a the information associated with a service account. 
        # Credential impertantent information is to be stored in encrypted forms and decrypted by a key provided to a user upon the initial creation of master account.