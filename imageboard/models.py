from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.timezone import now
from easy_thumbnails.fields import ThumbnailerImageField
from embed_video.fields import EmbedVideoField
from imageboard.storage import MediaFileStorage
import hashlib

PAGINATION_CHOICES = (
	( 5, '5' ),
	( 10, '10' ),
	( 15, '15' ),
	( 20, '20' )
)
COMMENT_FILTER_CHOICES = (
	( 5, '5' ),
	( 10, '10' ),
	( 20, '20' ),
	( 50, '50' )
)
ACTIVITY_CHOICES = (
	( 0, 'Disabled' ),
	( 10, '10' ),
	( 20, '20' )
)
NIGHTMODE_CHOICES = (
	( False, 'Off'),
	( True, 'On' )
)


class Post(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length=200)
	image = ThumbnailerImageField(storage=MediaFileStorage(), blank=False)
	media = EmbedVideoField(blank=True, null=True)
	body = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(editable=False, db_index=True, default=now)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if self.image:
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


class Comment(models.Model):
	user = models.ForeignKey(User)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	image = ThumbnailerImageField(storage=MediaFileStorage(), blank=True)
	media = EmbedVideoField(blank=True, null=True)
	body = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return 'Comment for: %s' % self.post.title

	def save(self, *args, **kwargs):
		if self.image:
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

		if not self.created: # New Comment
			self.post.modified = now()
			self.post.save()

		super(Comment, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		# Change modified on parent Post
		p = self.post
		if p.comment_set: # Post has comments
			c = p.comment_set.exclude(id=self.id).last()
			if c: # Last comment
				p.modified = c.created
				p.save()
			else: # No comments after deletion
				p.modified = p.created
				p.save()

		super(Comment, self).delete(*args, **kwargs)


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	pagination = models.PositiveSmallIntegerField(default=10, blank=False, choices=PAGINATION_CHOICES)
	comment_filter = models.PositiveSmallIntegerField(default=10, blank=False, choices=COMMENT_FILTER_CHOICES)
	activity = models.PositiveSmallIntegerField(default=10, blank=False, choices=ACTIVITY_CHOICES)
	nightmode = models.BooleanField(default=False, blank=False, choices=NIGHTMODE_CHOICES)

	def __str__(self):
		return 'Profile of user: %s' % self.user.username

	# Create a UserProfile for the new user upon account creation
	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			UserProfile.objects.create(user=instance)
