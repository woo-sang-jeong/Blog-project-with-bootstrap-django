from django import forms
from .models import Post
from .models import Comment

from django_summernote.widgets import SummernoteWidget

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
        widgets = {'content': SummernoteWidget()}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
