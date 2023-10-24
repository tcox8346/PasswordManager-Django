from typing import Any, Optional
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .models import Post, Comment
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.urls import URLPattern
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
# Create your views here.
class ForumHomeView(ListView):
    model = Post
    context_object_name = 'all_Posts'
    template_name = 'MessageBoard/forumhome.html'
    
    
class PostCreateView( LoginRequiredMixin, CreateView,):
    model = Post
    template_name = 'MessageBoard/post_create.html'
    fields = ['title','body']
    success_url = reverse_lazy('forumhome')
    #Automatic field fill
    def form_valid(self,form):
        form.instance.author = self.request.user
        return super().form_valid(form)
class PostModifyView(UpdateView,LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    context_object_name = 'activepost'
    template_name = 'MessageBoard/post_update.html'
    fields = ['body']
    
    def form_valid(self, form):
        return super().form_valid(form)

    
class PostDetailView(DetailView):
    model = Post
    template_name = 'MessageBoard/post.html'
    context_object_name = 'post_info'
class PostDeleteView(DeleteView,LoginRequiredMixin ,UserPassesTestMixin):
    model = Post
    success_url = reverse_lazy('forumhome')
    def test_func(self):
        obj = self.get_object()
        return obj.author ==self.request.user
   
class CommentCreateView(LoginRequiredMixin,CreateView):
    model = Comment
    template_name = 'MessageBoard/comment_create.html'
    fields = ['body']
    #TODO - Replace with lazy link to post being commented on
    success_url = reverse_lazy('forumhome')
    def form_valid(self,form):
        #If form is valid, auto fill author and post fields
        form.instance.author = self.request.user
        form.instance.post = Post(self.kwargs['pk'])
        # return to post when complete
        self.success_url = form.instance.post.get_absolute_url()
        return super().form_valid(form)
class CommentModifyView(UpdateView,LoginRequiredMixin ,UserPassesTestMixin):
    model = Comment
    def form_valid(self, form):
        form.instance.post = Post(self.kwargs['pk'])
        self.success_url = form.instance.post.get_absolute_url()
        return super().form_valid(form)
    def test_func(self):
        obj = self.get_object()
        return obj.author ==self.request.user
    def get_object(self, queryset) :
        id = self.kwargs()
        return super().get_object(queryset)