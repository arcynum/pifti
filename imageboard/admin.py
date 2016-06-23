from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from imageboard.models import Post, Comment, UserProfile
import time


class PostAdmin(admin.ModelAdmin):
	fields = ['title', 'body', 'media']
	actions = ['delete_selected', 'update_modified', 'update_image_attributes']

	list_display = ('id', 'user', '__str__', 'created', 'modified')

	def save_model(self, request, obj, form, change): 
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

	def delete_selected(self, request, obj):
		""" Override default admin method to call model delete function """

		for p in obj:
			p.delete()

		if obj.count() == 1:
			message = "1 post was"
		else:
			message = "%s comments were" % obj.count()

		self.message_user(request, "%s successfully deleted." % message)

	delete_selected.short_description = "Delete selected posts"

	def update_modified(self, request, obj):
		""" Updates the modified date for a selected list of posts """

		for p in obj:
			if p.comment_set.count() > 0: # Post has comments
				p.modified = p.comment_set.last().created
				p.save()
			else: # Post has no comments
				p.modified = p.created
				p.save()

		if obj.count() == 1:
			message = "1 post was"
		else:
			message = "%s posts were" % obj.count()

		self.message_user(request, "%s successfully updated." % message)

	update_modified.short_description = \
		"Update selected posts modified date"

	def update_image_attributes(self, request, obj):
		""" Forcefully updates image attributes for a selected list of posts

		WARNING: May use excessive amounts of system memory when batch updating
        multiple images at once if exotic libraries are in use (bug #48).
		"""
		posts = obj.count()

		for i, p in enumerate(obj, start=1):
			if p.image:
				etime = time.time()
				p.image.set_image_attributes()
				# Updating multiples?
				if i < posts:
					# Minimum of 250ms for each image update
					while time.time() < etime + 0.25:
						time.sleep(0.01)

		if posts == 1:
			message = "1 post was"
		else:
			message = "%s posts were" % obj.count()

		self.message_user(request, "%s successfully updated." % message)

	update_image_attributes.short_description = \
		"Update selected posts image attributes"


class CommentAdmin(admin.ModelAdmin):
	fields = ['post', 'body', 'media']
	actions = ['delete_selected', 'update_image_attributes']

	list_display = ('id', 'user', 'post', 'body', 'created')

	def save_model(self, request, obj, form, change):
		try:
			obj.user
		except ObjectDoesNotExist:
			obj.user = request.user

		obj.save()

	def delete_selected(self, request, obj):
		""" Override default admin method to call model delete function """

		for c in obj:
			c.delete()

		if obj.count() == 1:
			message = "1 comment was"
		else:
			message = "%s comment were" % obj.count()

		self.message_user(request, "%s successfully deleted." % message)

	delete_selected.short_description = "Delete selected comments"

	def update_image_attributes(self, request, obj):
		""" Updates the image attributes for a selected list of comments

        WARNING: May use excessive amounts of system memory when batch updating
        multiple images at once if exotic libraries are in use (bug #48).
        """
		comments = obj.count()

		for i, c in enumerate(obj, start=1):
			if c.image:
				etime = time.time()
				c.image.set_image_attributes()
				# Updating multiples?
				if i < comments:
					# Minimum of 250ms for each image update
					while time.time() < etime + 0.25:
						time.sleep(0.01)

		if comments == 1:
			message = "1 comment was"
		else:
			message = "%s comments were" % obj.count()

		self.message_user(request, "%s successfully updated." % message)

	update_image_attributes.short_description = \
		"Update selected comments image attributes"


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
