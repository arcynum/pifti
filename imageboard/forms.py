from django import forms
from imageboard.models import Post, Comment

class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'media', 'image', 'body']

class PostEditForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['body',]

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ['image', 'media', 'body']

class CommentEditForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['body',]