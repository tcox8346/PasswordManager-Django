from django.views.generic import CreateView, DetailView, FormView, ListView
from models import FriendRequest
from forms import FriendRequestForm
from UserManagement.models import SolutionUserProfile, SolutionUser
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


def ViewFriendRequest(DetailView,LoginRequiredMixin):
    template = ''
    context_object_name = 'request_record'
    
    def accept(self):
        pass
    def decline(self):
        pass
    
def ListFriendRequests(ListView, LoginRequiredMixin):
    template = ''
    context_object_name = 'request_records'
    
def CreateFriendRequest(CreateView, LoginRequiredMixin):
    template = ''
    context_object_name = 'request_record'
    
    
def FriendRequestFormView(FormView,LoginRequiredMixin):
    """This View is never reached manually, it is automatically populated with information from CreateFriendRequest View with the requester: the current user and recipient: a string denoting the name of the user that is requested to be added as a friend"""
    template = ''
    context_object_name = 'request_record'
    form_class = FriendRequestForm
    
    def form_valid(self, form):
        self.generate_request( self.request.user,form.cleaned_data['recipient'])
        return super.form_valid(form)
    
    def generate_request(self, requester_user_account:SolutionUser, recipient_username:str):
        """Generates a new Friend Request Record \n Returns True is successful"""
        try:       # get current users profile
            user_profile = SolutionUserProfile.objects.get(user=requester_user_account)
            # get recipient profile 
            if SolutionUser.objects.filter(username=recipient_username).exists():
                recipient_account = SolutionUser.objects.get(username=recipient_username)
                recipient_profile = SolutionUserProfile.objects.get(user = recipient_account)
                
                # Determine if record doesnt already exists, and if recipient is not already a friend
                if not FriendRequest.objects.filter(requester=user_profile, recipient = recipient_profile, request_state=False) and not user_profile.check_friends(recipient_username):
                    
                    # if not Create a draft record
                    draft_request = FriendRequest(requester=user_profile, recipient = recipient_profile)
                
                    # Save result
                    draft_request.save()
            else:
                #Return false if friend target doesnt exists
                return False
        except print("An error has occured during request generation"):
           return False
 

        return True
    
    