from django.db import models
from django.contrib.auth.models import User
from easy_thumbnails.fields import ThumbnailerImageField

class Post(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length = 200)
	image = ThumbnailerImageField(upload_to = 'up', blank = False)
	body = models.TextField()
	created = models.DateTimeField(auto_now_add = True)
  
  	def __unicode__(self):
  		return self.title

	class Meta:
		permissions = (
			('can_edit_own', 'Can edit own posts'),
			('can_delete_own', 'Can delete own posts')
		)
  
class Comment(models.Model):
	user = models.ForeignKey(User)
 	post = models.ForeignKey(Post)
 	image = ThumbnailerImageField(upload_to='up')
 	body = models.TextField()
 	created = models.DateTimeField(auto_now_add = True)

 	def __unicode__(self):
 		return 'Comment for: %s' % self.post.title

 	class Meta:
		permissions = (
			('can_edit_own', 'Can edit own comments'),
			('can_delete_own', 'Can delete own comments')
		)