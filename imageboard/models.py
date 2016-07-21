from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from embed_video.fields import EmbedVideoField
from imageboard.fields import ThumbnailerExtField
from imageboard.storage import MediaFileStorage
import hashlib

IMAGES_HELP_TEXT = _('Images and WEBM/MP4. Limit: 5MB.')
EMBED_VIDEO_HELP_TEXT = _('Youtube, Vimeo, Soundcloud, '
						  'Streamable, Dailymotion, and Gfycat.')


class Post(models.Model):
	user = models.ForeignKey(
		User
	)
	title = models.CharField(
		max_length=200
	)
	image = ThumbnailerExtField(
		storage=MediaFileStorage(),
		blank=False,
		help_text=IMAGES_HELP_TEXT
	)
	media = EmbedVideoField(
		_('media url'),
		blank=True,
		null=True,
		help_text=EMBED_VIDEO_HELP_TEXT
	)
	body = models.TextField()
	created = models.DateTimeField(
		auto_now_add=True
	)
	modified = models.DateTimeField(
		editable=False,
		db_index=True,
		default=now
	)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		"""
		Generate image name hash.
		"""
		if self.image and not self.id: # New Post with image
			md5 = hashlib.md5()
			while True:
				data = self.image.read(128)
				if not data:
					break
				md5.update(data)
			image_hash = md5.hexdigest()
			image_extension = self.image.name.split('.')[-1]
			image_name = image_hash + '.' + image_extension
			self.image.name = image_name

		super(Post, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		"""
        Delete post and comments, including the post image source, attributes,
        and thumbnail.
        """
		# Iterate over and delete comments
		comments = self.comment_set.all()
		for c in comments:
			c.delete(post_delete=True)

		# Delete and cleanup post image references
		if self.image:
			name = self.image.name.lstrip('./') # Ensure naming standard
			duplicates = Post.objects.filter(image__icontains=name).count()
			duplicates += Comment.objects.filter(image__icontains=name).count()
			# Do not delete if there are multiple references to this source
			if duplicates <= 1:
				self.image.delete()

		super(Post, self).delete(*args, **kwargs)


class Comment(models.Model):
	user = models.ForeignKey(
		User
	)
	post = models.ForeignKey(
		Post,
		verbose_name=_('parent post'),
		on_delete=models.CASCADE
	)
	image = ThumbnailerExtField(
		storage=MediaFileStorage(),
		blank=True,
		help_text=IMAGES_HELP_TEXT
	)
	media = EmbedVideoField(
		blank=True,
		null=True,
		help_text=EMBED_VIDEO_HELP_TEXT
	)
	body = models.TextField()
	created = models.DateTimeField(
		auto_now_add=True
	)

	def __str__(self):
		return 'Comment for: %s' % self.post.title

	def save(self, *args, **kwargs):
		"""
		Generate image name hash and update parent post modified.
		"""
		if not self.id: # New comment
			self.post.modified = now()
			self.post.save()

			if self.image: # Has image
				md5 = hashlib.md5()
				while True:
					data = self.image.read(128)
					if not data:
						break
					md5.update(data)
				image_hash = md5.hexdigest()
				image_extension = self.image.name.split('.')[-1]
				image_name = image_hash + '.' + image_extension
				self.image.name = image_name

		super(Comment, self).save(*args, **kwargs)


	def delete(self, post_delete=False, *args, **kwargs):
		"""
		Delete Comment including the comment image source, attributes, and
		thumbnail. Updates the parent post modified date when `post_delete`
		is False (default), indicating the parent post is not facing deletion.
		"""
		# Post has comments and post is not being deleted
		if self.post.comment_set and not post_delete:
			c = self.post.comment_set.exclude(id=self.id).last()
			# Update the parent post modified date
			if c: # Last comment
				self.post.modified = c.created
				self.post.save()
			else: # No comments after deletion
				self.post.modified = self.post.created
				self.post.save()

		# Delete and cleanup comment image references
		if self.image:
			name = self.image.name.lstrip('./') # Ensure naming standard
			duplicates = Post.objects.filter(image__icontains=name).count()
			duplicates += Comment.objects.filter(image__icontains=name).count()
			# Do not delete if there are multiple references to this source
			if duplicates <= 1:
				self.image.delete()

		super(Comment, self).delete(*args, **kwargs)


class UserProfile(models.Model):
	PAGINATION_CHOICES = (
		(5, '5'),
		(10, '10'),
		(15, '15'),
		(20, '20')
	)
	COMMENT_FILTER_CHOICES = (
		(5, '5'),
		(10, '10'),
		(20, '20'),
		(50, '50')
	)
	ACTIVITY_CHOICES = (
		(0, 'None'),
		(10, '10'),
		(20, '20')
	)

	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE
	)
	pagination = models.PositiveSmallIntegerField(
		default=10,
		blank=False,
		choices=PAGINATION_CHOICES,
		help_text=_('Number of posts per page.')
	)
	comment_filter = models.PositiveSmallIntegerField(
		default=10,
		blank=False,
		choices=COMMENT_FILTER_CHOICES,
		help_text=_('Number of revealed comments beneath posts.')
	)
	activity = models.PositiveSmallIntegerField(
		default=10,
		blank=False,
		choices=ACTIVITY_CHOICES,
		help_text=_('Items in the Latest Activity list.')
	)
	nightmode = models.BooleanField(
		default=False,
		blank=False,
		help_text=_('Toggle the dark website theme.')
	)

	def __str__(self):
		return 'Profile of user: %s' % self.user.username

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		"""
		Create a UserProfile for the new user upon account creation
		"""
		if created:
			UserProfile.objects.create(user=instance)


class SourceAttributes(models.Model):
	name = models.CharField(max_length=255, db_index=True)
	format = models.CharField(max_length=16, blank=True, null=True)
	animated = models.BooleanField(default=False, blank=False)

	def __str__(self):
		if self.animated:
			return "Animated " + self.format
		else:
			return self.format
