from collections.abc import Iterable
from typing import Any
from django.urls import reverse
from django.db.models import Q
from config.settings import USER_PROFILE_MODEL
# Validation Requirements
from django.core.exceptions import ValidationError
# Dispatcher Functionality
from django.dispatch import receiver
from django.db.models.signals import post_save

#Models

# TODO Decouple - make field settings.USER_PROFILE_MODEL
 
from django.db import models
from django.contrib.auth import get_user_model

SolutionUserProfile = USER_PROFILE_MODEL

# TODO validators 
def validate_requesttarget(value):
    request_target_user = get_user_model().objects.filter(username = value)
    if not SolutionUserProfile.objects.filter(request_target_user).exists() :
        raise ValidationError(("%(value) is does not exists"), params={"value": value})     
    

# Create your models here.
class FriendList(models.Model):
    owner_profile = models.OneToOneField(SolutionUserProfile, verbose_name=("friendlist_owner"), related_name=('friend_record_owner'),on_delete=models.CASCADE)
    friends_list = models.ManyToManyField(SolutionUserProfile, verbose_name=("friend_list_set"), related_name=('all_friends'), blank=True,)
    slug = models.SlugField(default='', unique=True)
    def __str__(self):
        return self.owner_profile.user.username
    
    # Core functions
    def get_friends(self):
        friends_string = []
        for friend in self.friends_list:
            friends_string.append(friend.user.username)
        
        return friends_string
    def add_friend(self, user_profile):
        if not self.b_is_friend(user_profile):  
            self.friends_list.add(user_profile)
        return
    def remove_friend(self, user_profile):
        if self.b_is_friend(user_profile):  
            self.friends_list.remove(user_profile)
        return
    
    # Helper functions
    def b_is_friend(self, user_profile):
        """accepts a user profile and determines if profile exists in current objects list of friend profiles"""
        # get list of friend profiles associated to self
        if user_profile in self.friends_list.all():
            # if user profile is in list return True
            return True
      
        # else return False
        return False
    def get_owner(self):
        return self.owner_profile
    
    def save(self, *args, **kwargs):
        if self.slug == '':
            self.slug = self.owner_profile.slug
        return super().save(*args, **kwargs)
class FriendRequest(models.Model): # Server Based Encryption
    requester = models.ForeignKey(SolutionUserProfile, related_name='requesting_user', on_delete=models.CASCADE) # Direct mapping to UserAccount entry
    request_target = models.ForeignKey(SolutionUserProfile, related_name='request_target', on_delete=models.CASCADE, validators=[])
    request_state = models.BooleanField(default=False, null=False) # State: active = 0 , inactive  = 1
    request_datetime = models.DateTimeField(auto_now_add=True)
    request_response = models.BooleanField(blank = True, null=True) # State: declined = 0 , accepted  = 1
    
    # Disallow repeat request for active request - TODO - set contraint to allow only one record with current constraint to be active at a time. 
        # This is to allow a user to request a friend again 
    class Meta:
        #unique together current constraint and request_state = False : active
        constraints = (models.UniqueConstraint(fields=['requester', 'request_target'], condition=Q(request_state=False), name="unique_freind_request"),)
        
       
    def get_absolute_url(self):
     return reverse("request_detail", kwargs={"pk": self.pk})
    
    # This classes functions all work on the premise of user profiles
    def process_request(self, is_accepted:bool, current_user_profile:SolutionUserProfile, testing = False):
        """Accepts a boolean and the user profile of the current user. \n Results in the manipulation of both the recipient and requesting user profiles friends list being updated if boolean is True \n This action is taken by the recipient of the request"""
        
        if testing:
            print(f"{is_accepted}, {current_user_profile == self.request_target}")
            
        if type(is_accepted) == bool and current_user_profile == self.request_target:
            # Get references to both user profiles connected friendslist
            recipient_friends_list:FriendList= FriendList.objects.get(owner_profile = self.request_target) 
            requester_friends_list:FriendList = FriendList.objects.get(owner_profile = self.requester) 
            # Fail safe incase user request present that already has recipient as friend
            if recipient_friends_list.b_is_friend(self.requester) or requester_friends_list.b_is_friend(self.request_target):
                #invalidate request
                print("Friend already exists on list, invalidating request")
                self.request_state = 1
                
            else:
                #if the request has been accepted 
                self.request_response = is_accepted
                
                if is_accepted == True:
                    try:
                        # add username of requester to recipient friends list
                        recipient_friends_list.add_friend(self.requester)
                    
                        # add username of recipient to  requester friends list
                        requester_friends_list.add_friend(self.request_target)
                    

                    
                    except Exception: 
                        print('An error has occured while modifying friendlist')
                        return 0
                    
                # When completed change request to inactive
                try:

                    print("saving changes to recipient friendlist")
                    recipient_friends_list.save()
                    print("saving changes to recipient friendlist")
                    requester_friends_list.save()
                
                except Exception:
                    print('An error has occured while accessing or changing a friend request')
                    return 0
                
            # update current state of request to complete and user response
            self.request_response = is_accepted
            self.request_state = True
            self.save()
            
            if testing == True:
                print(f'instance {self.pk}: modified')
            # If no errors have occured return True for complete status
            return 1
    def cancel_request(self, requester:SolutionUserProfile, testing = False):
        #TODO Decouple into own app   

        """Cancels request, This action is taken by the requester"""
        # if requester desires to cancel the friend request
        if requester == self.requester:
            # set request state to inactive
            self.request_state = 1
        
        if testing:
            print('request cancelation in progress')
        # save cancel state change
        self.save()
        if testing:
           print('request cancelation complete')
        
        # return value designating operation success
        return 1

   
# Signals - Reciever
# Dispatcher - Create FriendList when profile created
@receiver(post_save, sender=SolutionUserProfile)
def friendlist_create(sender, instance=None, created=False, **kwargs):
    if created:
        FriendList.objects.create(owner_profile=instance)
        print(f"user profile{instance.user.username}Friend List Instance Created")
        
