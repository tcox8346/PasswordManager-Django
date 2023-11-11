
from collections.abc import Iterable
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
#Mail Functionality
from django.core.mail import send_mail
# Token generation
from .tokens import TokenGenerator
# REquired functions
import secrets, datetime
from django.urls import reverse
from django.db.models import Q
from autoslug import AutoSlugField

# Signals
from django.dispatch import receiver
from django.db.models.signals import post_save



# custom fields - Profile

#encryption
from .fields import KEY_SIZE #, EncryptedText_Private, EncryptedField_Char, EncryptedField_EmailField
# encryption - server key


# models
class SolutionUserManager(UserManager):
    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        if not username:
            raise ValueError("username is required")
        user = self.model(email = email,username = username,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_user(self, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email,username, **extra_fields)
    
    def create_superuser(self, email=None, username=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email,username, **extra_fields)
    
class SolutionUser(AbstractUser, PermissionsMixin): # Server Based Encryption
    #For this solution the user password is instead a key automatically generated by the system upon registration which is sent to the user
    username = models.CharField(max_length=255, blank=False, unique=True, null=True) # seen by users - cannot be changed 
    email = models.EmailField(blank=False, unique=False, default="")
    #TODO- at a later date implement way to remove need for this field 
    password = models.CharField(max_length=1024, blank=False, unique=False, null=True)

    #password == master key of user, created by system upon registration - this value is a hash of the users actual key and used to confirm user defined master key
    key = models.CharField(max_length=KEY_SIZE, blank=False, unique=True, null=True)
    
    #control attribute - disabled when account is first logged in - deactivated when creating initial key
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=False, auto_now_add=True) 
    slug = AutoSlugField(populate_from='username', default='', unique=True)
    
    #Constraints  
    models.UniqueConstraint(fields=['username', 'email'], name= 'unique_account')
    
    #Authentication 
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email',]
    objects = SolutionUserManager()
    
    def __str__(self):
        return f"{self.username} {self.email}"
    def _create_key(self, size):
        #@ method that creates and returns a random key of a specific length, KEY_SIZE
        try:
            
            # generate a new key combo that is unique
            secret_key = self.generate_free_key()

            counter = 0 
            while SolutionUser.objects.filter(key=secret_key).exists() and counter < 5:
                # This version uses a randomly generated string of key_size length
                secret_key = secrets.token_hex(KEY_SIZE)
                counter += 1          
            
            print("new key generated")
            return secret_key
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            return None
    def create_masterkey(self):
        return self._create_key(KEY_SIZE)  
    def generate_free_key(self, key_size = KEY_SIZE):
        # generate a new key combo that is unique
        return secrets.token_hex(key_size)
  
    def email_user(self, subject: str, message: str,recipient_list: list,from_email: str = ..., **kwargs):
        send_mail(message=message, subject=subject, from_email=from_email, recipient_list=recipient_list)
        return 
    def create_profile(self,user_account ,key_size = KEY_SIZE):
        """Create User Profile, prepopulates fields: user, shared_key """
        try:
            # Check if profile already exists 
            if SolutionUserProfile.objects.filter(user=self).exists():
                return False
        except Exception:
            print(f"An error has occured while checking the user profile object")     
            return False
        
        try:    
            #Generate a possible share key 
            share_key= self.generate_free_key(key_size)  
                    
            #create  counters for retrying to create unique key
            counter = 0
            counter_limit = 10
            # Check if generated key is unique to SolutionUserProfile Table, if not redo up to x times
            while SolutionUserProfile.objects.filter(shared_key = share_key).exists():
                print("Shared Key Found in Record")
                if counter >= counter_limit:
                    print("Counter limit reached, unable to create a profile")
                    return False  
                
                counter += 1
                share_key= self.generate_free_key(key_size)
                
        except Exception:
            print(f"An error has occured while Generating a share key for new user profile object")  
            return False   

        
        try:
            # Create and Save profile record 
            new_profile = SolutionUserProfile.objects.create(user = user_account, shared_key = share_key, )
            new_profile.save()
        except Exception:
            print(f"An error has occured while creating user profile object")  
            return False  
        
        return True
    def get_key(self):
        """Returns the private key : 'key' attribute"""
        return self.key   
       
class Token(models.Model):
    tokenValue = models.CharField(max_length=50, blank = True, null = True, unique=True)
    owner = models.ForeignKey(get_user_model(), verbose_name=("TokenOwner"), on_delete=models.CASCADE)
    activeState = models.IntegerField(default=0, blank = True)
    activeTimeFrame = models.DurationField(null = True, default = datetime.timedelta(hours=10))
    
    ActiveStates = {"useable": 0, "used": 1}
    def deactivateToken(self):
        self.active = self.ActiveState["useable"]
    def activateToken(self):
        self.active = self.ActiveState["used"]
    def generateToken(self):
        #Create a token of x length
        try:
            newToken = TokenGenerator(self.owner)
            self.tokenValue = newToken
        except Exception:
            print("A Token has been generated that already exists")
            
            for i in range(5):
                newToken = TokenGenerator(self.owner)
                result = Token.objects.filter(tokenValue = newToken).exists()
                if not result:
                    self.tokenValue = newToken
                    return
            print(f"A New Token Value unable to be created for user {self.owner.username}")
        return
    def bisValid(self):
        # TODO - Impemenent time based validity checking - activeTimeFrame : latest date-time in which token is implicitly valid
        if self.active == 0:
            return True
        return False
    def reset_token(self):
       
        try:
            # create new tokenValue, distinct
            self.generateToken()
            # Change token state to usable
            self.deactivateToken()
            # Send email containing new token and link to users email
        
        except Exception:
            pass
        return
   
class SolutionUserProfile(models.Model): # Server - User Based Encrpytion
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
    user = models.OneToOneField(get_user_model(), related_name='profile_owner', on_delete=models.CASCADE)
    image = models.ImageField(blank=True,upload_to=None, height_field=20, width_field=20, max_length=None)
    
    # $ Encrypted using Server key
    shared_key = models.CharField(max_length=KEY_SIZE) # A Encryption key used to encrypt and decrypt Credential Records marked as shared by the user, 256 byte key    
    # $ Encrypted using user key
    shared_keys = models.TextField(blank=True,default="" ) # A Dictionary in csv form . example : "username=value, username=value,..."         #@ Encrypt
    
    slug = models.SlugField(default='', unique=True)

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...):
        if self.slug == '':
            self.slug = self.user.slug
        if self.shared_key == '':
            self.shared_key = self.generate_key()
        super().save()
    def get_absolute_url(self):
        return f"{self.user.username}/profile/"

    def update_image(self,image):
        #type check image, only allow jpg for testing - Must be filtered to allow files up to a safe size with no sql code
        if type(image) == None:
            pass
        self.image = image
        print(f'user: {self.user.get_username()} has updated their image')  
        return    
    def generate_key(self):
        # generate a new key combo that is unique
        new = secrets.token_hex(KEY_SIZE) 
        
        counter = 0
        counter_limit = 10
        # while generated key exsists in model table remake it
        while SolutionUserProfile.objects.filter(shared_key = new).exists():
            # after 10 iterations stop operation and return false if no unique key could be generated
            if counter < counter_limit:
                print(f"Unique share key could not be generated for user {self.user.get_username}")
                return ''
            new = secrets.token_hex(KEY_SIZE) 
            
            
            
        return secrets.token_hex(KEY_SIZE)
    def get_shared_key(self):
        return self.shared_key
    def get_user_key(self):
        return self.user.get_key()

    
    
    
    
# Signals
@receiver(post_save, sender=SolutionUser)
def create_profile(sender, instance=None, created=False, **kwargs):
    if created:
        SolutionUserProfile.objects.create(user=instance)
        print(f"user{instance.username} profile created")
        
"""
Encrpytion Based Functionality
@receiver(post_save, sender=SolutionUserProfile)
def on_profile_creation(sender, instance=None, created=False, **kwargs):
    if created:
        update_encryption_keys_on_creation(instance)
    instance.save() 
 
def update_encryption_keys_on_creation(instance=None):
    if instance == None:
        return
    instance_object = SolutionUserProfile.objects.get(instance)
    instance_user_key = instance_object.user.key
    instance_object.shared_keys = EncryptedText_Private(instance_user_key)    
"""      








