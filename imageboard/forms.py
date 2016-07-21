from django import forms
from imageboard.models import Post, Comment, UserProfile


class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'image', 'media', 'body']


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
		model = Comment
		fields = ['body',]


class ProfileEditForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['pagination', 'comment_filter', 'activity', 'nightmode']
		labels = {
			'comment_filter': 'Comment Filter',
			'nightmode': 'Night Mode',
        }
