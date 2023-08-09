from django.contrib import admin
from .models import Comment, Post

class CommentInLine(admin.StackedInline):
    model= Comment
    extra = 0

class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInLine,]
# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)