from typing import Any
from django.http import HttpResponse
from .models import SolutionUser, SolutionUserProfile, Token
from .tokens import account_activation_token 
from django.contrib.auth.tokens import default_token_generator
from .forms import UserCreationForm, UserChangeForm, AccountDeleteForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, View, DetailView, FormView, TemplateView
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.utils.encoding import force_bytes, force_str 



 #CSS Themes - Change if not using bootstrap
THEMES = {'night': 'data-bs-theme="dark"', 'day':'data-bs-theme="light"',}
# Create your views here.

# Secure Views

class CredentialPasswordChangeView(auth_views.PasswordChangeView, LoginRequiredMixin):
    template_name = 'UserManagement/change-password.html' 
    success_url= reverse_lazy('home')
    form_class = PasswordChangeForm
    
        
    def form_valid(self, form):
        user = SolutionUser.objects.get(username=self.request.user.username)
        user_token_record = Token.objects.get(owner = user)
        if user_token_record._state == user_token_record.ActiveStates['useable']: 
            user_token_record.deactivateToken()
            # Testing code - remove for production
            print(f'{user.username} token deactivated: password change')

        return super().form_valid(form)
class DeleteView(FormView, LoginRequiredMixin):
    template_name = 'UserManagement/accountdelete.html'
    form_class = AccountDeleteForm
    success_url = reverse_lazy('logout')
    
    def form_valid(self, form):
        user = SolutionUser.objects.get(username = self.request.user.username)
        user.is_active = False
        return super().form_valid(form)   
class SettingsView(TemplateView, LoginRequiredMixin):
    template_name = 'UserManagement/settings.html'


#@ TODO
class ProfileDetailView(DetailView, LoginRequiredMixin):
    model = SolutionUserProfile
    template_name = 'UserManagement/ProfileTemplates/userprofile.html'
    context_object_name = 'profile_info'
        

# Public Views
class SignupView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home') 
    template_name = 'registration/signup.html'      
    
    def form_valid(self, form):
        
        #Generate Users  account and secret keys - master and recovery
        self.model_instance = form.save(commit=False)
        new_passwordandkey = self.set_passandkey()
        self.model_instance.save()
        
        #Generate Users Activation Token
        
        token = account_activation_token.make_token(self.model_instance)
        while Token.objects.filter(tokenValue = token).exists():
             # determine if record is unique, if not create a new token for user
            token = account_activation_token.make_token(self.model_instance)
            continue

            
        # store activation token in useable state
        token_record = Token.objects.create(tokenValue = token, owner = self.model_instance)
        token_record.save()

        
       
        #Email Activation 
        current_site = get_current_site(self.request)
        subject = 'Account Activation'
        
        # Generate email to send to new user
        message = render_to_string('registration/acc_active_email.html',{
            'user': self.model_instance,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(self.model_instance.pk)),
            'token': token,
            'password': new_passwordandkey,
        })    
        recipient_list = [self.model_instance.email]
        

        #email user 
        self.model_instance.email_user(subject=subject, message=message, recipient_list=recipient_list) 

        
        return super().form_valid(form) 
    def activate(request, uidb64, token):
        #Email Validation - Account Validation 
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = SolutionUser._default_manager.get(pk=uid)
        except(TypeError, ValueError, OverflowError, SolutionUser.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            user_token_record = Token.objects.get(user=user.pk)
            #activate token so user can use it to login
            user_token_record.activateToken()
            user_token_record.save()
            return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        else:
            return HttpResponse('Activation link is invalid!')     
    def set_passandkey(self):
        """Generates unique master key and sets initial record to have master key hash as password. Used only during initilzation of a record"""
        # This function generates 2 keys and stores one as the user master key and the other as the user password
        count_limit = 5
        count = 0
        
        masterkey = SolutionUser.create_masterkey(self.model_instance)
        #initially the password is the master key so only need to check if one such value exists
        key_exists = SolutionUser.objects.filter(key = masterkey).exists()
        
        #-----------------------------------------------------------------------------------------#
        if key_exists and masterkey is not None:
            while True:
                try:
                
                    #Generate new combinations until unique values generated
                    masterkey = SolutionUser.create_masterkey(self.model_instance)
                        
                    #increase control counter
                    count += 1
                    
                    #if controll counter passed defined limit force exit operation and inform user/operator
                    if count >=count_limit:
                        print(f"Could not generate a unique password set after {count_limit} attempts")
                        raise Exception
                    continue
                except masterkey == None:
                    template = "Exception new_key calculated to be None or no unique key could be generated\n"
                    
                    print (template)
                    break
        #-----------------------------------------------------------------------------------------#
        
        #set user password as confirmed unique new password
        self.model_instance.password = make_password(masterkey)
        #set user key as confirmed unique new key - Hash for security
        self.model_instance.key = masterkey 
        
        # return source key for usage
        return masterkey              
class SigninView(LoginView):
    #success_url = reverse_lazy('home')    
    template_name = 'registration/login.html'
    form_class = UserChangeForm
    def form_valid(self, form):
            
        response = super().form_valid(form)
        if response.session['current_theme'] == '':
            response.session['current_theme'] = THEMES['day']
            
        return response
class ActivateAccountView(View):   
    """View accessed when user first logs into system after registration, includes user profile creation"""
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = SolutionUser.objects.get(pk=uid)
            print(f'user is {user.username}')
        except (TypeError, ValueError, OverflowError, SolutionUser.DoesNotExist):
            user = None

        user_token_record = Token.objects.get(owner = user)
        if user is not None and account_activation_token.check_token(user, token) and user_token_record.activeState == user_token_record.ActiveStates['useable']:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, ('Your account have been confirmed. Your Master key -ie your protection code- has been generated and sent to your provided email address'))
                
            return redirect(reverse_lazy('user_change_password'))
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('invalid_view')
        
    def SetupUserProfile(self, user:SolutionUser):
        """Sets up SolutionUserProfile for user upon successful registration \n Returns True upon successful creation of profile"""
        try:
            # Initialize users profile with base information
            b_profile_creation_success = user.create_profile(user)
            
        
        except Exception:
            print("An error has occured while setting up user profile")
            return b_profile_creation_success 
        
        return b_profile_creation_success

#@ TODO Complete Email based password Reset Functionality 
class CredentialPasswordResetView(auth_views.PasswordResetView):
    template_name = 'UserManagement/change-password.html' 
class CredentialPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'UserManagement/reset_confirm.html'    
class CredentialPasswordResetDoneView(auth_views.PasswordResetDoneView ):
    template_name = 'UserManagement/reset-done.html'   
class CredentialPasswordResetCompleteView(auth_views.PasswordResetCompleteView ):
    template_name = 'UserManagement/reset_complete.html' 
    success_url= reverse_lazy('home')
    
class InvalidTokenView(TemplateView):
    template_name = 'UserManagement/invalidrequest.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["error_string"] = 'This is an invalid request, your token has already been used. If this is an error please send a account reset request, or login if you know your password or master password'

        return context
# function view that generates a new activation token    
