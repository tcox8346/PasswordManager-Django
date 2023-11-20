from typing import Any
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

class CredentialRecord(models.Model):
    # Usermanagement record that specifies the user who owns the record
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='credentials', to_field='username') 
       # Service feild: This fields holds what service is tied to the credential record, i.e the service provider of the credential
    service_provider = models.CharField(blank=True,default='Undefined', max_length=50)
    username = models.CharField(blank=False, max_length=50) #@ Encrypt
    password =  models.CharField(blank=False, max_length=50, default=None, null=True)  #@ Encrypt - Derive a model class that uses a key provided by user to encrpyt and decrypt
    email = models.EmailField(blank=True, null=True, default=None) #@ Encrypt # An optional field that denotes the email address associated with the record
    Share_state = (('Public','shared'), ('Private','unshared')) # Specifier that designates if a record is shared to friend profiles
    
    # Service choices stores a value that denotes the class of record. For example
        # if the record is for business purposes, personel, or undefined.
    ## The Service type is a a way of grouping service records by purpose, it uses the choices of the above type.
    service_type = models.CharField(choices=Share_state, default= Share_state[0] ,blank=True, max_length=50)
    #Shares field: This field holds a collection of string values that designate the usernames that can access a credentials fields. This will be in csv form
        #TODO: implement model methods that return csv as list
    
    added_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    access_granted_to = models.TextField(default='') # Holds list of usernames who have one time access to a resource - the name is removed when access is provided
    requesting_access = models.TextField(default='')
    class Meta:
       constraints = [models.UniqueConstraint(fields=['service_provider', 'username', 'owner'], name="unique_service_username_owner")]
        
    def get_absolute_url(self):
        return reverse("credential_detail", kwargs={"user": self.owner.user.get_username() ,"pk": self.pk})
    def __str__(self):
        return f'credential record: {self.pk}'
    
    # Notification subfunctionality
    def request_for_access(self, requester:str):
        # create a notification to owner of record that the requester desires access to the record
        Notification.objects.create(purpose = 0, active = True,
                                    description = f"User {requester}  requests access to the credential set {self.service_provider}: {self.username} : {self.password} ", 
                                    associated_user = self.owner, other_user = requester ,urgency = True, related_credentail = self)
        # Create a notification to requester that they have requested access to the record
        Notification.objects.create(purpose = 8, active = True,
                                    description = f" You requested access to the credential set {self.service_provider}: {self.username} : {self.password} ", 
                                    associated_user = get_user_model().objects.get(username = requester), urgency = False, related_credentail = self)
        # add requester name to list of users requestng access to credential
        if requester not in self.list_users_requesting_access():
            self.requesting_access =  self.convert_list_to_csv(self._add_to_requestaccess_list(requester)) 
            self.save()         
    def notify_owner_passwordchangerequired(self):
        # creates a urgent notification that the owner needs to change their password of the credential set
        Notification.objects.create(purpose = 4, 
                                    description = f"The credential set {self.service_provider}: {self.username} : {self.password} has been shared with a removed user, change it now so they do not access your account ", 
                                    associated_user = self.owner, urgency = True)
    def provide_access(self, username):
        """
        add friend name to access_granted_to 
        """
        if username in self.list_users_requesting_access():
            self.access_granted_to = self.convert_list_to_csv(self._add_to_access_list(username)) 

            # Create notification that access has been provided to the user
            create_credentialaccessgranted_notificaiton(self.owner, username, self)

        return
    def remove_access(self,username):
        """
        remove friend name to access_granted_to - called when a user on access granted to list accesses the object
        """
        if username in self.list_granted_access_users():
            self.access_granted_to = self.convert_list_to_csv(self._remove_from_access_list(username)) 
            self.save()
            create_credentialaccessgranted_notificaiton(self.owner, username, self)
        return
    def list_users_requesting_access(self):
        """seperate string into a list of usernames"""
        result = []
        current = ""
        if self.requesting_access == None:
            return result
        for char in self.requesting_access:
            # if char is a comma, insert current into list and reset current to blank string
            if char == ",":
                result.append(current)
                current = ""
            # add char to current
            current += char
        return result
    def list_granted_access_users(self):
        """seperate string into a list of usernames"""
        result = []
        current = ""
        for char in self.access_granted_to:
            # if char is a comma, insert current into list and reset current to blank string
            if char == ",":
                result.append(current)
                current = ""
            # add char to current
            current += char

        return result
    def convert_list_to_csv(self, access_list):
        """Convert list into csv string, list taken in must not have values with trailing commas"""
        #convert new corewords list into csv
        new_csv:str = ''
        for word in access_list:
            new_csv += word + ','
        return new_csv   
    def _add_to_access_list(self,username):
        
        current_access = self.list_granted_access_users()
        if username not in current_access:
            current_access.append(username)
            self.access_granted_to = self.convert_list_to_csv(current_access)
            self.save()
        else:
            print('user already has access')
        return 
    def _remove_from_access_list(self, username):
        current_access = self.list_granted_access_users()
        current_access.remove(username)
        
        return current_access
    def _add_to_requestaccess_list(self,username):
        current_access = self.list_users_requesting_access()
        current_access.append(username)
        # iterate over list and remove '' entries
        for word in current_access: 
            if word == '' or word == ',':
                current_access.remove
        self.requesting_access = self.convert_list_to_csv(current_access)
        self.save()
        return 
    def _flush_access_granted(self):
        print("flushing access ")
        self.access_granted_to = ''
        self.save()
    # Credentials are records of information that detail a the information associated with a service account. 
        # Credential impertantent information is to be stored in encrypted forms and decrypted by a key provided to a user upon the initial creation of master account.
        
# Notification Functionality 
class Notification(models.Model):
    """This is a notifcation in relation to the credential sharing system - this handles informing users of request to access a credential, and notifications to users about changing credentials"""
    
    notification_purpose = [('CredentialAccessRequest',0), ('CredentialAccessDenail',1), ('CredentialAccessAccepted',2), ('CredentialChangeRequired',3), ('CredentialChangeCompleted',4), 
                            ('CredentialRecordAdded',5),('CredentialRecordRemoved',6),('CredentialRecordModified',7),('CredentialRecordAccessed',8), ('CredentialAccessRequested',9)] # Specifier that designates if a record is shared to friend profiles
    activity_state = [('active', 0), ('inactive',1), ('silenced', 2)]
    
    # owning user of the notification
    associated_user = models.ForeignKey(get_user_model(), verbose_name=("notified_user"), on_delete=models.CASCADE)
    purpose = models.IntegerField(choices=notification_purpose, blank=False, unique=False)    
    description = models.TextField(max_length=500, unique=False, default="") 
    added_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    active = models.BooleanField(choices=activity_state, blank=False, unique=False, default=True)
    urgency = models.BooleanField(default=False ) #"Statues that denotes if a notification requires timely attention or not"
    # User connected to notification that isnt the owner
    other_user = models.CharField(max_length=100, verbose_name=("requesting_user"), default=None, null=True)
    related_credentail = models.ForeignKey(CredentialRecord, verbose_name=("related_credential_record"), on_delete=models.CASCADE)
    read = models.BooleanField(default=False) # Denotes if the owner has read the notification
    def provide_access(self):
        """Called when purpose is CredentialAccessAccepted"""
        if self.other_user == None:
            print("other user is none")
            return
        
        print("access being granted")
        #self.related_credentail._flush_access_granted()
        self.related_credentail._add_to_access_list(self.other_user)
        self.active = False
        print(f"new access list : {self.related_credentail.list_granted_access_users()}")
        # create notification that user has been provided access to the record
        create_credentialaccessgranted_notificaiton(self.associated_user, self.other_user, self.related_credentail)
        self.save()
    def access_granted(self):
        """Called when notification purpose is CredentialRecordAccessed"""
        if self.other_user == None or self.other_user not in self.related_credentail.list_granted_access_users():
            return
        self.related_credentail._remove_from_access_list(self.other_user)
        #create notification that x user has accessed the record
        create_credential_accessed_notificaiton(self.associated_user, self.other_user, self.related_credentail)
    def decline_access(self):
        self.active = self.activity_state['inactive']
        self.save()
        create_credential_access_denied_notificaiton(self.associated_user, self.other_user, self.related_credentail)
        
#Signals

@receiver(post_save, sender=CredentialRecord)
def create_credentialstored_notification(sender, instance=None, created=False, **kwargs):
    """Create a notification when a credential record is added to the system"""
    if created:
        Notification.objects.create(purpose = 5, 
                                    description = "A credential record has been added to your account", associated_user = instance.owner, related_credentail = instance)
    # else if credental already exist create a updated credential notification
    else:
        Notification.objects.create(purpose = 7, description = f"A credential record has been modified on your account: {instance.service_provider} : {instance.username}", associated_user = instance.owner, related_credentail = instance)

# Notification Creation Methods
def create_credentialaccessrequest_notificaiton(associated_user, requesting_user:str, related_credentail:CredentialRecord):
    new_notification = Notification.objects.create(purpose = 0, 
                                description = f"A credential record has been requested for access: Requester: {requesting_user} Credential: {related_credentail.service_provider} : {related_credentail.username}", 
                                associated_user = associated_user, other_user = requesting_user,
                                related_credentail = related_credentail)
def create_credentialaccessgranted_notificaiton(associated_user, requesting_user:str, related_credentail:CredentialRecord):
    new_notification = Notification.objects.create(purpose = 2, 
                                description = f"A credential record has been accessed by Requester: {requesting_user} Credential: {related_credentail.service_provider} : {related_credentail.username}. Access List: {related_credentail.list_granted_access_users()}", 
                                associated_user = associated_user, other_user = requesting_user,
                                related_credentail = related_credentail)   
def create_credential_accessed_notificaiton(associated_user, requesting_user:str, related_credentail:CredentialRecord):
    new_notification = Notification.objects.create(purpose = 8, 
                                description = f"A credential record has been accessed by Requester: {requesting_user} Credential: {related_credentail.service_provider} : {related_credentail.username}", 
                                associated_user = associated_user, other_user = requesting_user,
                                related_credentail = related_credentail)
def create_credential_access_denied_notificaiton(associated_user, requesting_user:str, related_credentail:CredentialRecord):
    new_notification = Notification.objects.create(purpose = 1, 
                            description = f"A credential record access request has been denied. Requester: {requesting_user} Credential: {related_credentail.service_provider} : {related_credentail.username}", 
                            associated_user = associated_user, other_user = requesting_user,
                            related_credentail = related_credentail)

