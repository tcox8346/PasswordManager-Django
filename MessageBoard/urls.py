from django.urls import path
from .views import ForumHomeView, PostCreateView ,PostDetailView, PostDeleteView, PostModifyView, CommentCreateView
urlpatterns = [
    path('', ForumHomeView.as_view(), name='forumhome'),
    path('post_new/', PostCreateView.as_view(), name ='post_new'),
    path('post/<int:pk>/', PostDetailView.as_view(), name ='post_detail'),
    #path('post/<int:pk>/comment', CommentDetailView.as_view(), name ='newpost'),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/update', PostModifyView.as_view(), name='post_update'),
    path('post/<int:pk>/commentnow', CommentCreateView.as_view(), name ='comment_new'),
     
]