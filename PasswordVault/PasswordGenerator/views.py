from typing import Any, Dict, Optional
from django import http
from django.forms.models import BaseModelForm,  ModelForm
from django.http import request
from django.shortcuts import render, redirect
from django.views.generic import FormView, RedirectView, TemplateView
from django.urls import reverse_lazy, reverse
from .models import PasswordGeneration
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PasswordGeneratorForm



# Constants
API_SERVICES = ['websterdictionary', 'websterthesaurus']
APIKEYS_WEBSTER = {"thesuarus": "b86db3b6-5ec2-4c31-88dd-0e49c3b04aea", "dictionary": "27537b3c-670c-44fa-bfd9-5f917c2cb7e3"}
#example of a functional api request
    #https://dictionaryapi.com/api/v3/references/thesaurus/json/food?key=b86db3b6-5ec2-4c31-88dd-0e49c3b04aea

# Create your views here.
 
#this view displayes the generic password settings such as the minimum length, the words that are core , etc
class PasswordGeneratorHomeView(TemplateView, LoginRequiredMixin):
    template_name = 'PasswordGenerator/dictionary_home.html'
    context_object_name = 'user_passwordgeneration_settings'
    
    
    #include list of used words in context of template
    def get_context_data(self, **kwargs: Any):
        #Create/ and or get a users PasswordGeneration settings record
        generator_result = PasswordGeneration.objects.get_or_create(owner=self.request.user,)
        self.user_password_generator = generator_result[0]
        context = super(PasswordGeneratorHomeView, self).get_context_data()
        #print(self.user_password_generator.list_core_words())
        userwords =  self.user_password_generator.list_core_words()
        context['user_words'] =userwords
        #print(self.view_core_list)
        context['minimum_word_count'] = self.user_password_generator.minimum_words
        context['generator'] = self.user_password_generator
        return context
              
class UpdateDictionaryFormView(FormView, LoginRequiredMixin):
    context_object_name = 'PasswordGenerator_context'
    template_name = 'PasswordGenerator/dictionary_add.html'
    form_class = PasswordGeneratorForm  
    
    #@ TODO - On Form Submission - Call methods on users PasswordGeneration object
    def form_valid(self, form: Any):
        password_generator:PasswordGeneration = PasswordGeneration.objects.filter(owner=self.request.user,)
        # - check if user submitted word is can be added to core dictionary
        print('password_generator retrieved')
        if password_generator.bCan_add_word(form.cleaned_data['word']):
            #- if yes, call functions that add word to core dictionary
            print('Atempting to update dictionary')
            password_generator.update_dictionaries(form.cleaned_data['word'], APIKEYS_WEBSTER['dictionary'], APIKEYS_WEBSTER['thesuarus'])
            # Save changes 
            password_generator.save()
            # - if successful redirect user to password generator home page
        else:
            print('word already exists')
            
        self.success_url = reverse_lazy('generator_home', kwargs={'user': self.request.user.username})
        return super().form_valid(form)
class PasswordGeneratorDeleteWord(RedirectView, LoginRequiredMixin):
    def get_redirect_url(self, *args: Any, **kwargs: Any):
        self.url = reverse_lazy('generator_home', kwargs={'user': self.request.user.username})
        
        # - check if user submitted word is can be added to core dictionary
        password_generator = PasswordGeneration.objects.get(owner=self.request.user,)
        password_generator.update_dictionaries(self.kwargs["word"],APIKEYS_WEBSTER['dictionary'], APIKEYS_WEBSTER['thesuarus'],b_remove=True)
       
        return super().get_redirect_url(*args, **kwargs)
class GeneratePasswordView(RedirectView, LoginRequiredMixin): 
    def get_redirect_url(self, *args: Any, **kwargs: Any):
        self.url = reverse_lazy('generator_home', kwargs={'user': self.request.user.username})
        try:
            #Generate a random password using the users password manager
            password_generator = PasswordGeneration.objects.get(owner=self.request.user)
            generated_password = password_generator.generate_string()
            print(f'generated value: {generated_password}')
            # store generated value in users session - this is shown on users home settings template
            self.request.session['recent_password_generated'] = generated_password
        except:
            print('An error has occured while creating a password for user')
        return super().get_redirect_url(*args, **kwargs)
 

class TestAPIView(TemplateView):
    """View that test api call - This variant test webster dictionary thesuarus for the word 'food' """
    template_name ='PasswordGenerator/Testing/testingAPI.html'
    
    def get_context_data(self, **kwargs: Any):
        #Test Dictionary Response
        self.TESTWORD = 'Do'

        if  not PasswordGeneration.objects.filter(owner=self.request.user).exists():
            print("User not found - Test API View")
            return context
        
        # Test response

        PasswordGenerator_instance =  PasswordGeneration.objects.get(owner=self.request.user)

        API_from_model = PasswordGenerator_instance.get_API_request_json(API_SERVICES[1], self.TESTWORD, APIKEYS_WEBSTER['thesuarus'])
        
        context = super(TestAPIView, self).get_context_data()
        context['api_json_list_full'] = []
        context['api_json_topic'] = []
        context['api_json_synonyms'] = []
        context['api_json_antonyms'] = []
        
        # if api call successful
        if API_from_model:  
            parsed_json_list = API_from_model
            #Testing - Accessing Dictionary data from response
            
            # Testing - if meta isnt in json request then word doesnt exists or there are no related words for it
            if 'meta' in parsed_json_list[0]: 
                
                # Select Topic Word
                print(f"Topic :{parsed_json_list[0]['meta']['id']}")
                context['api_json_topic']  = parsed_json_list[0]['meta']['id']
                
                # Select synonyms from provided response
                
                synonyms = parsed_json_list[0]['meta']['syns']
                if synonyms:
                    # correct synonyms refernce if provided double layer list 
                    if type(synonyms[0]) == list:
                        synonyms =  synonyms[0]
                    print(f"json response using 0 meta ,syns, 0 as key {synonyms}")
                    if len(synonyms) > 0:
                        context['api_json_synonyms'] = synonyms
                
                # Select antonyms from provided response
                antonyms = parsed_json_list[0]['meta']['ants'] 
                if antonyms :
                    # determine if antonym list is single layer 
                    if type(antonyms[0]) == list:
                        antonyms =  antonyms[0]
                    if len(antonyms) > 0:
                        context['api_json_antonyms'] = antonyms
                        print(f"json response using 0 meta ,ants as key {antonyms}")
            
            context['api_json_list_full'] = parsed_json_list 

        return context
class TestFlushView(RedirectView, LoginRequiredMixin):
    
    def get_redirect_url(self, *args: Any, **kwargs: Any):
        self.url = reverse_lazy('generator_home', kwargs={'user':self.request.user.username})
        self.PasswordGenerator = PasswordGeneration.objects.get(owner=self.request.user)
        print(f'Words being flushed \n Core: {self.PasswordGenerator.dictionaryCore} \n related: {self.PasswordGenerator.dictionaryRelated} ')
        self.PasswordGenerator.flush_dictionaries()
        print('Redirect for TestFlushView Called')
        return super().get_redirect_url(*args, **kwargs)
    
class ReminderView(TemplateView):
    #Views with templates use template_name to determine the html page that will be used
    template_name ='PasswordGenerator/Testing/testing.html'
    
    # Almost all pages have a url or success_url member
    
    # access a model object by using the modelname.objects: this is a manager for the object
    
    # access a url variable by using self.kwargs['name'] 
        #you can store values in cookies or sessions for permenant storage
    
     