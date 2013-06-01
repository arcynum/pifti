from imageboard.models import Post, Comment
from django.contrib import admin

class CommentInline(admin.TabularInline):
  	model = Comment
  	fields = ('body',)
  	extra = 1

class PostAdmin(admin.ModelAdmin):
  	fields = ('title', 'body',)
  	inlines = [CommentInline]

	def save_model(self, request, obj, form, change): 
	    obj.user = request.user
	    obj.save()

	def save_formset(self, request, form, formset, change): 
	    if formset.model == Comment:
	        instances = formset.save(commit = False)
	        for instance in instances:
	            instance.user = request.user
	            instance.save()
	    else:
	        formset.save()

admin.site.register(Post, PostAdmin)
