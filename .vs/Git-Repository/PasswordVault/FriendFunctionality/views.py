from typing import Any
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FriendRequest, FriendList
from django.views.generic import FormView, DetailView,ListView, View
from .forms import FriendRequestForm_CheckUsername

from django.contrib.auth import get_user_model
# Todo - find approach to decoucple direct model imports
from UserManagement.models import SolutionUserProfile
from CredentialVault.models import CredentialRecord, Notification
# JSON Functionality
from django.http import JsonResponse
import json

# Create your views here.
# Friend Functionality 
class ViewFriendListHome(DetailView, LoginRequiredMixin):
    template_name = 'FriendFunctionality/friend_list_detail.html'
    context_object_name = 'friend_record'
    model = FriendList
    
            
    def get_queryset(self):
        return super().get_queryset()
    
class CreateFriendRequestView(LoginRequiredMixin, FormView):
    """This View is never reached manually, it is automatically populated with information from CreateFriendRequest View with the requester: the current user and recipient: a string denoting the name of the user that is requested to be added as a friend"""
    
    template_name = "FriendFunctionality/friend_request_form.html"
    context_object_name = 'request_record'
    form_class = FriendRequestForm_CheckUsername
    
    
    def generate_request(self, requester_user, recipient_username:str): 
        """Generate Request and creates Friend Request Record, Must be called after validation"""
        
        # Try 
        try:
            # determine if neccessary App| Profile Table is present
            if  type(get_user_model()) == None:
                
                raise Exception   
        except Exception:
            print(f'Profile Functionality Not Provided - Unable To Process Request - user class must exist')
       
        try:    
            # Define Reciepient of request
            # get profile of recipient
            requested_account = get_user_model().objects.get(username = recipient_username)
            requested = SolutionUserProfile.objects.get(user = requested_account)   
            # Define Requester 
                # get user profile of current user
            friend_requester = SolutionUserProfile.objects.get(user = requester_user) 

            
            # Determine if an active request already exists matching the given parameters
            if FriendRequest.objects.filter(requester = friend_requester, request_target = requested, request_state=False):
                raise Exception(print(f"Friend Request Already Active For Users {requested_account.get_username()} | {self.request.user.get_username()}"))
            
            # Generate new FriendRequest 
            FriendRequest.objects.create(requester = friend_requester, request_target = requested)
        # if exception raised return False
        except Exception:
            print(f'An error has occured while generating a FriendRequest')
            return False
     
            
        # Return True if Successful
        return True
    
    def form_valid(self, form):
        # When form is submitted and valid
        if form.is_valid() and self.request.user.username != form.cleaned_data['requested_user']:
            # if form user isnt the current user
            self.generate_request(self.request.user ,form.cleaned_data['requested_user'])
            
            
        return super().form_valid(form) 

    def get_success_url(self):
            # Redirect to detail view when complete
        return reverse_lazy('user_friend_list', kwargs={'user': self.request.user, 'slug': self.request.user.slug})
    
class ViewFriendRequests(ListView, LoginRequiredMixin):
    template_name = 'FriendFunctionality/all_friend_requests.html'
    context_object_name = 'request_records'
    model = FriendRequest
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        user_profile = SolutionUserProfile.objects.get(user= self.request.user)
        context['request_results'] = FriendRequest.objects.filter(request_target = user_profile, request_state = False).all()
        context['user_requests'] = FriendRequest.objects.filter(requester = user_profile, request_state = False).all()
        
        return context

# View Friend Credential Records List View - Display only record owner - username, and password
class ViewFriendSharedCredentials(ListView, LoginRequiredMixin):
    """View ran by users who are seeing the shared list of their friends"""
    template_name = 'FriendFunctionality/shared_credentials.html'
    context_object_name = 'credential_records'
    model = FriendRequest
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        # get user profile
        user_profile = SolutionUserProfile.objects.get(user= self.request.user)
        # get user friend list
        friendList = FriendList.objects.get(owner_profile=user_profile)
        
        # get all credential records marked as shared owned by friends
        all_friends_shared_list = []
        all_friends_shared_list_viewable = []
        for friend_profile in friendList.friends_list.all():
            # Get all friend records that are shared
            credentialsets = CredentialRecord.objects.filter(owner = friend_profile.user, service_type = 'Public').all()
            # go through each record and add the records in which the user has access to view into viewable list
            if credentialsets != None:
                for credential_set in credentialsets:
                    # if the users username is in the credentials list of users with access
                    if self.request.user.username in credential_set.list_granted_access_users():
                        
                        # add the record to viewable
                        all_friends_shared_list_viewable.append(credential_set)
                        # remove user from access list of record after load load - This is to enforce one time viewing permission
                        credential_set.remove_access(self.request.user.username)
                        continue
                # otherwise add to standard shared list
                    all_friends_shared_list.append(credential_set)
    
                
        context['friend_credentials_hidden'] = all_friends_shared_list 
        context['friend_credentials_viewable'] = all_friends_shared_list_viewable 
        return context

def processFriendRemoval(request, *args, **kwargs):
    """View request that enables the removal of a friend from the authenticated users friends list"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # load json request data
        jsonData = json.loads(request.body)
        # get user instance from request
        user = jsonData.get('user_instance')
        # get name of user to remove  from freinds lst of user instance
        user_response = jsonData.get('user_to_remove')
        # get user profile and remove 
        user_profile = SolutionUserProfile.objects.filter(user)
        if user_profile.exists():
            #check if user friend list exists
            user_friendlist = FriendList.objects.filter(owner_profile = user_profile)   
            if user_friendlist.exists():
                #remove the friend from friends list
                user_friendlist.remove_friend(user_response)       
        is_success ={"successes?": None}
        return JsonResponse({'successful_execution': is_success})

# Class View Version of process friend request
#@method_decorator(csrf_exempt, name='dispatch')
class ProcessFriendRequestClassView(View, LoginRequiredMixin):
    
    def __init__(self, *args,**kwargs: Any):
        super().__init__(*args, **kwargs)       
    
    # code that handles post requests   
    def post(self, request, *args, **kwargs):
        # if ajext request 
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("Call properly recieved")
            result = self.generate_response()
        return JsonResponse({'response': result}, status = 200)
    
    # determine what actions are to be enacted on model instance
    def generate_response(self, *args, **kwargs):
        if  self.request.method == "POST":    
            """View The Request for friendship and allow user to accept or decline the request"""
            
            
            #Get the instance information for processing
            instance_pk = self.request.POST.get('request_id')
            # get friend request instance
            request_instance = FriendRequest.objects.get(pk=instance_pk)
            
            # check if purpose of response is to cancel request
            purpose = self.request.POST.get('purpose')
            print(purpose)
             # get the current users profile
            current_user_profile = SolutionUserProfile.objects.get(user = self.request.user)
            if purpose == 'cancel_request':
                request_instance.cancel_request(current_user_profile)
            
            else:
                # get user response boolean by converting userresponse string to its interger form, then to its boolean form
                instance_uservalue = bool(int(self.request.POST.get('user_response')))
                # process the request 
                request_instance.process_request(instance_uservalue, current_user_profile, False)
            return True
        else:
            # if the request isnt post return false
            return False
           
# Process Notification 
class ProcessCredentialAccessRequestClassView(View, LoginRequiredMixin):
    """Request Access to a credential Record - Generates a notification for the owner of the credential to inform that access request is waiting"""
    def __init__(self, *args,**kwargs: Any):
        super().__init__(*args, **kwargs)       
    
    # code that handles post requests   
    def post(self, request, *args, **kwargs):
        # this variation uses request.POST[] instead of json.load()
        # if ajext request 
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            user_requesting_access = request.POST['user_instance']
            user_response = request.POST['purpose']
            credential_subject = request.POST['request_id']
            if user_response == "access_request":
                # create a notification for access request owned by the owner of the credential subject and one for the requester
                CredentialRecord.objects.get(pk=credential_subject).request_for_access(user_requesting_access)
            
            
        return JsonResponse({'response': 'success'}, status = 200)
        
class NotificationListView(ListView, LoginRequiredMixin):
    """View that allows users to see the notifcation records owned by their accounts that are active"""
    template_name = 'FriendFunctionality/notifications.html'
    context_object_name = 'notification_records'
    model = Notification
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
       
        all_access_requests_notifications = []
        # get all active notification records owned by user
        all_active_notifications = Notification.objects.filter(associated_user = self.request.user, active = True).all()
        # mark the first x - amount that can be read at a time - as read
        
            
        for notification in all_active_notifications:
            # if the notification is about credential access requests store in context variable storing all credential requests
            if notification.purpose == 0:
                all_access_requests_notifications.append(notification)
                notification.read = True
                notification.save()
    
        context['access_requests'] = reversed(all_access_requests_notifications)
        context['all_notifications'] =  reversed(all_active_notifications)
        
        # Track all unread notifications
        unread_notifications = Notification.objects.filter(associated_user=self.request.user, read=False).count()
        context["unread_notifications"] = unread_notifications

        return context

def process_notification_accessrequest_response(request, *args, **kwargs):
    """Accepts or decline the request for credential access 0 owner of credential bound option"""
    
    is_success ={"successes?": None}
    # if ajext request 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            request_instance = request.POST['request_id']
            user_response = request.POST['purpose']
            
            # get notification object - request access
            notification = Notification.objects.get(pk = request_instance)

            # call accept or decline request based on user_response
            if user_response == "accept_request":
                notification.provide_access()
            else:
                notification.decline_access()
            is_success ={"successes?": True} 
            
            # set notification for requesting access to read and inactive
            notification.read = True
            notification.active = False
            notification.save() 
            
        # catch and print any exception that may be found
        except Exception as e: 
            print(f"error: {e}\n\n")
            is_success ={"successes?": False} 
        
            
        
    return JsonResponse({'successful_execution': is_success},status=200)

def remove_friend_json(request, *args, **kwargs):
    """Accepts or decline the request for credential access 0 owner of credential bound option"""
    
    is_success ={"successes?": None}
    # if ajext request 
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            friend_username = request.POST['user_to_remove']
            user_response = request.POST['purpose']
            user_instance = request.POST['user_instance']
            # get users friendlist
            FriendList_instance = FriendList.objects.get(owner_profile = (SolutionUserProfile.objects.get(user = user_instance)))
           

            # call accept or decline request based on user_response
            if user_response == "remove_friend":
                # get friend profile to remove
                friend_profile_to_remove = SolutionUserProfile.objects.get(user = (get_user_model().objects.get(username = friend_username)))
                FriendList_instance.remove_friend(friend_profile_to_remove)
                #Create a notification the the friend has been removed
                
                # print some indicator that the operation has occured
                print("frined removal successful")
            is_success ={"successes?": True} 
            
            
        # catch and print any exception that may be found
        except Exception as e: 
            print(f"error: {e}\n\n")
            is_success ={"successes?": False} 
        
            
        
    return JsonResponse({'successful_execution': is_success},status=200)
  
# Testing Views
class AJAXConnectionTestingView(View):
    def __init__(self, *args,**kwargs: Any):
        super().__init__(*args, **kwargs)
        
        
    # code that handles post requests   
    def get(self, request, *args, **kwargs):
        # if ajext request 
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'message': 'Successful Call with AJAX'})
        
        return JsonResponse({'message': 'call made'})