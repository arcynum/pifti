from django import forms
from imageboard.models import Post, Comment, UserProfile

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

class ProfileEditForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['pagination', 'comment_filter', 'activity', 'nightmode']
		labels = {
            'pagination': 'Posts Per Page:',
			'comment_filter': 'Comments Per Post:',
			'activity': 'Items In Latest Activity:',
			'nightmode': 'Night Mode:'
        }