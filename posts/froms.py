from django import forms
from .models import Post, Comment


class PostFrom(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'photo']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }
