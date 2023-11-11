from django.urls import path
from .views import ViewFriendListHome, CreateFriendRequestView,ViewFriendRequests, ProcessFriendRequestClassView, AJAXConnectionTestingView, processFriendRemoval

# Patterns are prepinned with user:str/friends/
urlpatterns = [
    #Every url begins with <str:username>
    path('<slug:slug>', ViewFriendListHome.as_view(), name ='user_friend_list'),
    path('NewFriendRequest/', CreateFriendRequestView.as_view(), name ='make_friend_request'),
    path('<slug:slug>/active_requests/', ViewFriendRequests.as_view(), name ='all_active_request'),
    path('process_request/', ProcessFriendRequestClassView.as_view(), name ='process_request'),
    path('remove_friend/', processFriendRemoval, name ='process_request_friend_removal'),
    # Alternative path to above
    #path('testing', AJAXConnectionTestingView.as_view(), name ='ajax_test'),
    #path('a', ClassView.as_view(), name ='name'),
    #path('a', ClassView.as_view(), name ='name'),

]