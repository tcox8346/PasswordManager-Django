from django.db import models
from UserManagement.models import SolutionUserProfile


# Create your models here.
class FriendRequest(models.Model):
    requester = models.ForeignKey(SolutionUserProfile, related_name='requesting_user', on_delete=models.CASCADE) # Direct mapping to UserAccount entry
    request_target = models.ForeignKey(SolutionUserProfile, related_name='request_target', on_delete=models.CASCADE)
    request_state = models.BooleanField(default=False, null=False) # State: active = 0 , inactive  = 1
    request_datetime = models.DateTimeField(auto_now_add=True)
    request_response = models.BooleanField(blank = True, null=True) # State: declined = 0 , accepted  = 1
    
    # Disallow repeat request for active request - TODO - set contraint to allow only one record with current constraint to be active at a time. 
        # This is to allow a user to request a friend again 
    class Meta:
        constraints = [models.UniqueConstraint(fields=['requester', 'request_target'], name="unique_freind_request")] 
            #unique together current constraint and request_state = 0
       
    #def get_absolute_url(self):
     #   return reverse("model_detail", kwargs={"pk": self.pk})
    
    # This classes functions all work on the premise of user profiles
    def process_request(self, is_accepted, current_user_profile:SolutionUserProfile):
        """Accepts a boolean and the user profile of the current user. \n Results in the manipulation of both the recipient and requesting user profiles friends list being updated if boolean is True"""
        if type(is_accepted) == bool and current_user_profile == self.request_target:
            #if the request has been accepted 
            self.request_response = is_accepted
            
            if is_accepted == True:
                try:
                    
                    recipient = current_user_profile
                    requester = self.requester
                    
                    # add username of requester to recipient friends list
                    recipient.add_friend(requester)
                
                    # add username of recipient to  requester friends list
                    requester.add_friend(recipient)
                
                   
                except Exception: 
                    print('An error has occured while modifying friendlist')
                    return 0
                
                
            # When completed change request to inactive
            try:
                self.request_response = is_accepted
                self.request_state = True
            
            except Exception:
                print('An error has occured while accessing or changing a friend request')
                return 0
            
            # If no errors have occured save the changes to the record
            self.save(commit=True)
            return 1
    def cancel_request(self, requester_profile:SolutionUserProfile):
        # if requester desires to cancel the friend request
        if requester_profile == self.requester:
            # set request state to inactive
            self.request_state = 1
        
        # save cancel state change
        self.save(commit = True)
        # return value designating operation success
        
        return 1
            