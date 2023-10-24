from django.urls import path
from .views import CredentialCreateView, CredentialDetailView, CredentialDeleteView, CredentialUpdateView, CredentialListView
urlpatterns = [
    #Every url begins with <str:username>
    path('', CredentialListView.as_view(), name ='credential_list'),
    path('new/', CredentialCreateView.as_view(), name ='credential_new'),
    path('<int:pk>/', CredentialDetailView.as_view(), name ='credential_detail'),
    path('<int:pk>/update', CredentialUpdateView.as_view(), name ='credential_update'),
    path('<int:pk>/delete', CredentialDeleteView.as_view(), name ='credential_delete'),
    
    #path('applykey/', ApplyKeyView.as_view(), name ='key_add'),

]