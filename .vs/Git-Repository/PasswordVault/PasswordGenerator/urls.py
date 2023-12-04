from django.urls import path
from .views import UpdateDictionaryFormView, PasswordGeneratorHomeView, PasswordGeneratorDeleteWord,GeneratePasswordView
from .views import TestAPIView,TestFlushView
#@ This allows two options - to view a users password generation settings and to update said settings
# Base patter is .../<username>/
urlpatterns = [
    #generator home view
    path('generation_preferences/', PasswordGeneratorHomeView.as_view(), name ='generator_home'),
    #generator update preferences
    path('update_generation_preferences/<pk>/', UpdateDictionaryFormView.as_view(), name ='generator_update'),
    #a page that initiates a call to the passed users password managers function that removes a word from core words valu. Immideate redired to home redirect when completede
    path('update_generation_preferences/remove/<str:word>/', PasswordGeneratorDeleteWord.as_view(), name ='delete_word'),
    # A page that automatically redirects to home view after completing a task
    path('generate_word/', GeneratePasswordView.as_view(), name ='generate_string'),

    #Testing Paths
    path('testpage/API/', TestAPIView.as_view(), name ='testing_api'),
    path('testpage/flush/', TestFlushView.as_view(), name ='testing_flush'),
    
]