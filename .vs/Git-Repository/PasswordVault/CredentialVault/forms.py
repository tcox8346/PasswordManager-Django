from django import forms

class MasterPasswordForm(forms.Form):
    master_key = forms.CharField(max_length=255, required=True)