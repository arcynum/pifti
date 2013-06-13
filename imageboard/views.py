from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from imageboard.models import Post, Comment
from imageboard.forms import PostForm, PostEditForm, CommentForm, CommentEditForm
import hashlib

@login_required
def index(request):
	post_list = Post.objects.prefetch_related('comment_set').all().order_by('-id')
	paginator = Paginator(post_list, 5)

	page = request.GET.get('page')
	try:
		post_list_paginated = paginator.page(page)
	except PageNotAnInteger:
		post_list_paginated = paginator.page(1)
	except EmptyPage:
		post_list_paginated = paginator.page(paginator.num_pages)

	return render(request, 'home.html', { 'post_list': post_list_paginated })

@login_required
def add_post(request):
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = Post()
			post.title = form.cleaned_data['title']
			post.body = form.cleaned_data['body']
			post.user = request.user

			if 'image' in request.FILES:
				image = request.FILES['image']
				md5 = hashlib.md5()
				while True:
					data = image.read(128)
					if not data:
						break
					md5.update(data)
				image_hash = md5.hexdigest()

				image_extension = image.name.split('.')[-1]
				image_name = image_hash + '.' + image_extension
				image.name = image_name
				post.image = image

			post.save()
			return HttpResponseRedirect(reverse('index'))
	else:
		form = PostForm()

	return render(request, 'post/add.html', { 'form': form })

@login_required
def edit_post(request, post_id):
	p = get_object_or_404(Post, pk = post_id)

	if request.method == 'POST':
		form = PostEditForm(request.POST, instance = p)
		form.save()

		return HttpResponseRedirect(reverse('index'))

	else:
		if p.user.is_superuser or p.user.is_staff:
			form = PostEditForm(instance = p)
		else:
			return HttpResponseRedirect(reverse('index'))

	return render(request, 'post/edit.html', { 'form': form })

@login_required
def delete_post(request, post_id):
	p = get_object_or_404(Post, pk = post_id)
	comments = Comment.objects.select_related().filter(post = p.id)

	for comment in comments:
		delete_specific_comment(comment.id)

	p.image.delete()
	p.image.delete_thumbnails()
	p.delete()

	return HttpResponseRedirect(reverse('index'))

@login_required
def add_comment(request, post_id):
	if request.method == 'POST':
		form = CommentForm(request.POST, request.FILES)
		if form.is_valid():
			comment = Comment()
			post = get_object_or_404(Post, pk = post_id)
			comment.post = post
			comment.body = form.cleaned_data['body']
			comment.user = request.user

			if 'image' in request.FILES:
				image = request.FILES['image']
				md5 = hashlib.md5()
				while True:
					data = image.read(128)
					if not data:
						break
					md5.update(data)
				image_hash = md5.hexdigest()

				image_extension = image.name.split('.')[-1]
				image_name = image_hash + '.' + image_extension
				image.name = image_name
				comment.image = image

			comment.save()
			return HttpResponseRedirect(reverse('index'))
	else:
		form = CommentForm()

	return render(request, 'comment/add.html', { 'form': form })

@login_required
def edit_comment(request, post_id, comment_id):
	c = get_object_or_404(Comment, pk = comment_id)

	if request.method == 'POST':
		form = CommentEditForm(request.POST, instance = c)
		form.save()

		return HttpResponseRedirect(reverse('index'))

	else:
		form = PostEditForm(instance = c)

	return render(request, 'comment/edit.html', { 'form': form })

@login_required
def delete_comment(request, post_id, comment_id):
	c = get_object_or_404(Comment, pk = comment_id)
	c.image.delete()
	c.image.delete_thumbnails()
	c.delete()

	return HttpResponseRedirect(reverse('index'))

def delete_specific_comment(comment_id):
	c = get_object_or_404(Comment, pk = comment_id)
	c.image.delete()
	c.image.delete_thumbnails()
	return

@login_required
def gallery(request):
	gallery_list = Post.objects.prefetch_related('comment_set').all().order_by('-id').exclude(image = '')
	return render(request, 'gallery/home.html', { 'gallery_list': gallery_list })

def logout_view(request):
    return logout_then_login(request, reverse('login'))
    # Redirect to a success page.
