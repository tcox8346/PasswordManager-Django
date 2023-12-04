from django.forms import Form
from .models import Post, Comment


class CommentForm(Form):
    class Meta:
        model = Comment
        fields = ("title",)
        
        
