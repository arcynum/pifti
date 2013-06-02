from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length = 200)
	image = models.ImageField(upload_to='up')
	body = models.TextField()
  
  	def __unicode__(self):
  		return self.title
  
class Comment(models.Model):
	user = models.ForeignKey(User)
 	post = models.ForeignKey(Post)
 	image = models.ImageField(upload_to='up')
 	body = models.TextField()

 	def __unicode__(self):
 		return 'Comment for: %s' % self.post.title