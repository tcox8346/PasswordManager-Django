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
    get_username.short_description = 'profile_owner'
    get_username.admin_order_field = 'profile__UserAccount'
    
    def get_friends(self, obj):
        return "\n".join([p.products for p in obj.friends_list.all()])
class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['requester', 'request_target']
    list_display = ['requester', 'request_target']
    search_fields = [' requester__username', 'request_target__username']
    class Meta:
     model = FriendRequest
     
     
     
admin.site.register(FriendList, FriendListAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)

