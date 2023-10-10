from django.urls import path
from .views import SignupView, ActivateAccountView, ProfileDetailView, DeleteView, SettingsView, CredentialPasswordChangeView, InvalidTokenView


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
]