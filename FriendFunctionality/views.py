from typing import Any
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FriendRequest, FriendList
from django.views.generic import FormView, DetailView,ListView, View
from .forms import FriendRequestForm_CheckUsername

from django.contrib.auth import get_user_model
# Todo - find approach to decoucple direct model imports
from UserManagement.models import SolutionUserProfile

# JSON Functionality
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
#@csrf_exempt
def ProcessFriendRequest(request, user, slug, pk, uservalue, data):
    """View The Request for friendship and allow user to accept or decline the request"""
    request_instance = FriendRequest.objects.get(pk=pk)
    request_instance.process_request(uservalue)
     
    return JsonResponse(statues=200 )

# Class View Version of process friend request

# @ decorator to ignore need for csrf_token - rework in working version to csrf token when called
#@method_decorator(csrf_exempt, name='dispatch')
class ProcessFriendRequestClassView(View, LoginRequiredMixin):
    
    def __init__(self, *args,**kwargs: Any):
        super().__init__(*args, **kwargs)
        
        
    # code that handles post requests   
    def post(self, request, *args, **kwargs):
        self.generate_response(*args,**kwargs)
        return HttpResponse("complete")

    def generate_response(self, *args, **kwargs):
        
        
        if  self.request.method == "POST":    
            """View The Request for friendship and allow user to accept or decline the request"""
            self.instance_pk = kwargs['pk']
            self.instance_uservalue = bool(kwargs['uservalue'])
            request_instance = FriendRequest.objects.get(pk= self.instance_pk)
            self.current_user_profile = SolutionUserProfile.objects.get(user=self.request.user)
            process_result = request_instance.process_request(self.instance_uservalue, self.current_user_profile)
        else:
            return HttpResponseBadRequest('Invalid request')
        