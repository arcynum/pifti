from imageboard.models import Post, Comment
from django.contrib import admin

class CommentInline(admin.TabularInline):
  model = Comment
  extra = 1

class PostAdmin(admin.ModelAdmin):
  fields = ['title', 'body']
  inlines = [CommentInline]

admin.site.register(Post, PostAdmin)
