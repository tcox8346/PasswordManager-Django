from django import forms

#Form associated with passwordgeneration model
class FriendRequestForm(forms.Form):
    recipient = forms.CharField(label='Insert A User Name Here', max_length=14)
    