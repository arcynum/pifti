from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from imageboard.models import Post, Comment, UserProfile

def update_modified(modeladmin, request, queryset):
	""" Updates the modified date for a selected list of posts """

	for p in queryset:
		if p.comment_set.count() > 0: # Post has comments
			p.modified = p.comment_set.last().created
			p.save()
		else: # Post has no comments
			p.modified = p.created
			p.save()
update_modified.short_description = "Update modified"


class PostAdmin(admin.ModelAdmin):
	fields = ['title', 'body']
	actions = [update_modified]

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
	fields = ['pagination', 'comment_filter', 'activity']

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile, ProfileAdmin)