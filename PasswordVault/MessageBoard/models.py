from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import MaxValueValidator

# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE, related_name='all_users')
    title = models.CharField(max_length=50, blank=False, null=False, default='Empty Title')
    body = models.TextField(max_length=500, blank=False)
    creation_date = models.DateField( auto_now=False, auto_now_add=True)
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})
    def __str__(self):
        return f'{self.author} : {self.title}'

class Comment(models.Model):
    author = models.ForeignKey(get_user_model(), verbose_name='Creater of the comment', on_delete=models.CASCADE, related_name='users')
    post = models.ForeignKey(Post, verbose_name='connected post object - ', related_name='comments',on_delete=models.CASCADE)
    body = models.TextField(max_length=500, blank=False, null=False)
    creation_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    likes = models.IntegerField(default=0, validators=[MaxValueValidator(9999999999)])
    dislikes = models.IntegerField(default=0, validators=[MaxValueValidator(9999999999)])
    
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.author.pk})
    def __str__(self):
        return f'{self.author} : {self.post.title}'