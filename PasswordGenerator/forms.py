from django import forms

#Form associated with passwordgeneration model
class PasswordGeneratorForm(forms.Form):
    word = forms.CharField(label='Try adding a word', max_length=14)
    b_delete = forms.BooleanField(label='Remove word',required=False)
class PasswordRequestForm(forms.Form):
   pass