from django.urls import path
from .views import ViewFriendListHome, CreateFriendRequestView,ViewFriendRequests, ProcessFriendRequestClassView,ProcessCredentialAccessRequestClassView,  ViewFriendSharedCredentials 
from .views import NotificationListView,  process_notification_accessrequest_response, processFriendRemoval, remove_friend_json

# Patterns are prepinned with user:str/friends/
urlpatterns = [
    #Every url begins with <str:username>
    path('<slug:slug>', ViewFriendListHome.as_view(), name ='user_friend_list'),
    path('NewFriendRequest/', CreateFriendRequestView.as_view(), name ='make_friend_request'),
    path('<slug:slug>/active_requests/', ViewFriendRequests.as_view(), name ='all_active_request'),
    path('process_request/', ProcessFriendRequestClassView.as_view(), name ='process_request'),
    path('remove_friend/', processFriendRemoval, name ='process_request_friend_removal'),
    path('friendrecords/', ViewFriendSharedCredentials.as_view(), name = "shared_friend_records"),
    path('notifications/', NotificationListView.as_view(), name = "notification_view"),
    #path('notifications-processing/', process_notification_accessrequest_response, name = "notification_handle_request"),
    # view that handles making a access request 
    path('notifications-requestaccess/', ProcessCredentialAccessRequestClassView.as_view(), name = "notification_credential_access_request"),
    # view that handles user response to an access request
    path('notifications-provide_access/', process_notification_accessrequest_response, name = "notification_handle_credential_access_request"),
    path('remove-friends/', remove_friend_json, name = "remove_friend"),

    # Alternative path to above
    #path('a', ClassView.as_view(), name ='name'),
    #path('a', ClassView.as_view(), name ='name'),

]