from imageboard.models import Post, Comment
from django.contrib import admin

from django.core.exceptions import ObjectDoesNotExist

class PostAdmin(admin.ModelAdmin):
  	fields = ['title', 'body']

	def save_model(self, request, obj, form, change): 
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

class CommentAdmin(admin.ModelAdmin):
  	fields = ['body']

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)