from django import forms

class PostForm(forms.Form):
	title = forms.CharField()
	image = forms.FileField(label='Select a file', help_text='Fuck you.', required=False)
	body = forms.CharField(widget = forms.Textarea)
