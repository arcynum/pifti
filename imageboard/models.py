from django.db import models
from django.contrib.auth.models import User
from easy_thumbnails.fields import ThumbnailerImageField
from embed_video.fields import EmbedVideoField
from imageboard.storage import MediaFileStorage
import hashlib

class Post(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length=200)
	image = ThumbnailerImageField(upload_to='uploads', storage=MediaFileStorage(), blank=False)
	media = EmbedVideoField(blank=True)
	body = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

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
	image = ThumbnailerImageField(upload_to='uploads', storage=MediaFileStorage(), blank=True)
	media = EmbedVideoField(blank=True)
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

		super(Comment, self).save(*args, **kwargs)