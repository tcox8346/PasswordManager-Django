from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, FormView
from .models import CredentialRecord as Credentials
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import CredentialVaultUserTestMixin
from .forms import MasterPasswordForm
from itertools import chain

#Requires friend app
from UserManagement.models import SolutionUserProfile

# Create your views here.
class CredentialDetailView(DetailView, LoginRequiredMixin):
    model= Credentials
    context_object_name = 'credential_record'
    template_name = 'CredentialVault/credential_detail.html'
  
class CredentialCreateView(CreateView, LoginRequiredMixin):
    model= Credentials
    fields = ['username', 'password', 'service_provider', 'service_type']
    context_object_name = 'credentail_record'
    template_name = 'CredentialVault/credential_new.html'
    
    def form_valid(self, form):
        # auto fill
        form.instance.owner = self.request.user     
        #store class global value that stores the newly created form  
        self.new_record = form.save(commit=False)
        
        # Encrypt provided password_secure field
            #savedform = form.save(commit=False)
            #plaintext = self.request.user.username.join(savedform.username).join(savedform.service).join(savedform.password_secure)
            #savedform.password_secure = self.new_record.test_encryption(plaintext)
        return super().form_valid(form)
    
    
    def get_success_url(self):
        # Redirect to detail view when complete
        return reverse_lazy('credential_detail', kwargs={'user': self.request.user, 'pk': self.new_record.pk})
    
    # TODO 
    def set_credentials(self, form):
        # Encrypt all fields with password that exists in user model
        pass
    
class CredentialListView(ListView, LoginRequiredMixin, CredentialVaultUserTestMixin):
    model= Credentials
    context_object_name = 'credential_records'
    template_name = 'CredentialVault/credential_home.html'
    
    def get_queryset(self):
        # Return only credentials owned by user
        return super().get_queryset().filter(owner=self.kwargs['user'])
      
class CredentialDeleteView(DeleteView, LoginRequiredMixin):
    model = Credentials
    template_name = 'CredentialVault/credential_confirm_delete.html'

    #TODO - Fix; required to follow ..'<str:user>/ url but uses generic .../pk path
    def get_success_url(self):
        success_url = reverse_lazy('credential_list', kwargs={'user': self.request.user.username})   
        return success_url
    
class CredentialUpdateView(UpdateView,LoginRequiredMixin):
    model= Credentials
    context_object_name = 'credential_record'
    template_name = 'CredentialVault/credential_update.html'
    fields = ['password', 'service_type']
    
    def form_valid(self, form):
        if form.is_valid():
            
            self.success_url = reverse_lazy('credential_detail', kwargs={'user': self.request.user.username, 'pk': self.kwargs['pk']})
        return super().form_valid(form)
    
    #Todo add strict methods that automatically create new credentials
    def suggest_password(self, form, length):
        #store old password
        #create a new password of a provided length
        #compare old and new passwords
        #if not the same return new password
            #else recreate new password 
        pass        
   
   
#Targeted Views
      
class SharedCredentialsView(ListView, LoginRequiredMixin):
    model= Credentials
    context_object_name = 'credential_records'
    template_name = 'CredentialVault/credential_home.html'
    
    def get_queryset(self):
        """Return only query set of friends in users friends list"""

        # Get User Profile
        user_profile:SolutionUserProfile = SolutionUserProfile.objects.get(user = self.kwargs['user']) 
        query_result = None
        #for each friend in users friends list
        for friend in user_profile.get_friends_list():
            # if query is just starting set result to 1st query
            if query_result == None:
                query_result =  super().get_queryset().filter(owner=friend, Share_state='shared') 
            #other wise append each friend result to query results
            query_result = list(chain(query_result, super().get_queryset().filter(owner=self.kwargs[friend], Share_state='shared') ))
            #return completed query
        return query_result

 
class ApplyKeyView(FormView):
    template_name = 'CredentialVault/userkey.html'
    form_class = MasterPasswordForm
    fields = ['master_key']
   
    def form_valid(self, form):
        response =  super().form_valid(form)
        # Setup Master Key provided by form in cookie title key 
        response.set_cookie("key", str(form.cleaned_data['master_key']))
        return response
    def get_success_url(self):
        #redirect to credential list view upon completion
        success_url = reverse_lazy('credential_list', kwargs={'user': self.request.user.pk})   
        return success_url
