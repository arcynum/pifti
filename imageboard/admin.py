from imageboard.models import Post, Comment, UserProfile
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
	fields = ['post', 'body']

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

class ProfileAdmin(admin.ModelAdmin):
	fields = ['pagination', 'activity']

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile, ProfileAdmin)