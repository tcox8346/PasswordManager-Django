from django.urls import path
from .views import SignupView, ActivateAccountView, ProfileDetailView, DeleteView, SettingsView, CredentialPasswordChangeView, InvalidTokenView, CreateFriendRequestView


    #All profile paths = accounts/...
    # active users = <username>/...
urlpatterns = [
    path('signup/', SignupView.as_view(), name ='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),
    path('delete/', DeleteView.as_view(), name='user_delete'),
    path('updatepassword/', CredentialPasswordChangeView.as_view(), name='user_change_password'),
    path('profile/', ProfileDetailView.as_view(), name='user_profile'),
    path('settings/', SettingsView.as_view(), name='user_settings'),
    path('error/', InvalidTokenView.as_view(), name='invalid_view'),
    #Every url begins with <str:username>
        # url to view a friend request detail view
    #path('<int:pk>', FriendRequestSubmissionForm.as_view(), name ='friendrequest'),
    # url to create a new friend request
    path('new/', CreateFriendRequestView.as_view(), name ='friendrequest_create'),
   
    
]