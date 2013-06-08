from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from imageboard.models import Post, Comment
from imageboard.forms import PostForm, CommentForm
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
def view_post(request, post_id):
	p = get_object_or_404(Post, pk = post_id)
	return render(request, 'post/view.html', { 'post': p })

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

def logout_view(request):
    return logout_then_login(request, reverse('login'))
    # Redirect to a success page.
