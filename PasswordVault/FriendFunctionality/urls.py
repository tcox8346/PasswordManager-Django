from django.urls import path
from .views import ViewFriendList, CreateFriendRequestView, ViewFriendRequest, ViewFriendRequests

# Patterns are prepinned with user:str/friends/
urlpatterns = [
    #Every url begins with <str:username>
    path('<slug:slug>', ViewFriendList.as_view(), name ='user_friend_list'),
    path('NewFriendRequest/', CreateFriendRequestView.as_view(), name ='make_friend_request'),
    path('<slug:slug>/active_request', ViewFriendRequest.as_view(), name ='active_request'),
    path('<slug:slug>/active_requests', ViewFriendRequests.as_view(), name ='all_active_request'),
    #path('a', ClassView.as_view(), name ='name'),

]