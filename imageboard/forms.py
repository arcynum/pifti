from django import forms
from imageboard.models import Post, Comment

class PostForm(forms.Form):
	title = forms.CharField()
	media = forms.CharField()
	image = forms.FileField(label = 'Select an image', required = True)
	body = forms.CharField(widget = forms.Textarea)

class PostEditForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['body']

class CommentForm(forms.Form):
	image = forms.FileField(label = 'Select a file', required = False)
	body = forms.CharField(widget = forms.Textarea)

class CommentEditForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['body']