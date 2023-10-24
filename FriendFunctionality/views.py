from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FriendRequest, FriendList
from django.views.generic import FormView, DetailView,ListView
from .forms import FriendRequestForm_CheckUsername

from django.contrib.auth import get_user_model
# Todo - find approach to decoucple direct model imports
from UserManagement.models import SolutionUserProfile

#from .forms import FriendRequestSubmissionForm

# Create your views here.
# Friend Functionality 
class ViewFriendList(DetailView, LoginRequiredMixin):
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
            friend_request = FriendRequest.objects.create(requester = friend_requester, request_target = requested)
            # Save Request
            friend_request.save()
        
        # if exception raised
        #return False
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
class ViewFriendRequest(DetailView,LoginRequiredMixin):
    """View The Request for friendship and allow user to accept or decline the request"""
    template_name = 'FriendFunctionality/friend_request.html'
    context_object_name = 'request_record'
    model = FriendRequest
    
    
    def accept(self):
        pass
    def decline(self):
        pass
    
class ViewFriendRequests(ListView, LoginRequiredMixin):
    template_name = 'FriendFunctionality/all_friend_requests.html'
    context_object_name = 'request_records'
    model = FriendRequest

   

    