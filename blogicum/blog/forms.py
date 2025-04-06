from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'location', 'pub_date', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control', 'rows': 3,
                    'placeholder': 'Комментарий...'
                }
            ),
        }
