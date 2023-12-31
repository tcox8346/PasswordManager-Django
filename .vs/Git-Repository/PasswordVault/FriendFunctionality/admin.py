from django.contrib import admin
from .models import FriendList, FriendRequest

# Register your models here.
class FriendListAdmin(admin.ModelAdmin):
    list_filter = ['owner_profile']
    list_display = ['get_username', 'get_friends']
    search_fields = ['user', ]
    class Meta:
        model = FriendList
        
    # Function that retrieves username from the objects stored owner profile
    def get_username(self, obj):
        return obj.owner_profile.user.username
    def get_friends(self,obj):
        friend_names = []
        for friend in obj.friends_list.all():
            friend_names.append(friend.user.username)
        
        return friend_names
    

class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['requester', 'request_target']
    list_display = ['get_username', 'get_request_target']
    search_fields = [' requester__username', 'request_target__username']
    class Meta:
     model = FriendRequest
    
    def get_username(self, obj):
        return obj.requester.user.username
    def get_request_target(self, obj):
        return obj.request_target.user.username
     
     
admin.site.register(FriendList, FriendListAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)

