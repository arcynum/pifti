from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from imageboard.models import Post, Comment, UserProfile


class PostAdmin(admin.ModelAdmin):
	fields = ['title', 'body']
	actions = ['update_modified']

	list_display = ('id', '__str__', 'created', 'modified')

	def save_model(self, request, obj, form, change): 
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

	def update_modified(self, request, obj):
		""" Updates the modified date for a selected list of posts """

		for p in obj:
			if p.comment_set.count() > 0:  # Post has comments
				p.modified = p.comment_set.last().created
				p.save()
			else:  # Post has no comments
				p.modified = p.created
				p.save()

		if obj.count() == 1:
			message = "1 post was"
		else:
			message = "%s posts were" % obj.count()

		self.message_user(request, "%s successfully updated." % message)

	update_modified.short_description = "Update selected posts modified date"


class CommentAdmin(admin.ModelAdmin):
	fields = ['post', 'body']
	actions = ['delete_selected']

	list_display = ('id', 'post', 'body', 'created')

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

	def delete_selected(self, request, obj):
		""" Override default admin method to call model delete functions """

		for c in obj:
			c.delete()

		if obj.count() == 1:
			message = "1 comment was"
		else:
			message = "%s comment were" % obj.count()

		self.message_user(request, "%s successfully deleted." % message)

	delete_selected.short_description = "Delete selected comments"


class ProfileAdmin(admin.ModelAdmin):
	fields = ['pagination', 'comment_filter', 'activity', 'nightmode']

	list_display = ('user', 'pagination', 'comment_filter', 'activity', 'nightmode')

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile, ProfileAdmin)
