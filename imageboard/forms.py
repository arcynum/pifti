from django import forms

class PostForm(forms.Form):
	title = forms.CharField()
	image = forms.FileField(label = 'Select an image', required = True)
	body = forms.CharField(widget = forms.Textarea)

class CommentForm(forms.Form):
	image = forms.FileField(label = 'Select a file', required = False)
	body = forms.CharField(widget = forms.Textarea)