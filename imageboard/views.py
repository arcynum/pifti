from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from imageboard.models import Post, Comment
from imageboard.forms import PostForm, PostEditForm, CommentForm, CommentEditForm
from imageboard.storage import MediaFileStorage
from django.contrib.auth.forms import AuthenticationForm
import hashlib

from pprint import pprint

@login_required
def index(request):
	post_list = Post.objects.prefetch_related('comment_set').all().order_by('-id')
	paginator = Paginator(post_list, 10)

	page = request.GET.get('page')
	try:
		post_list_paginated = paginator.page(page)
	except PageNotAnInteger:
		post_list_paginated = paginator.page(1)
	except EmptyPage:
		post_list_paginated = paginator.page(paginator.num_pages)

	# Adjusting the paginator rendering results for quicker paging.
	previous_previous_page_number_exists = False
	next_next_page_number_exists = False
	previous_previous_page_number = None
	next_next_page_number = None

	if post_list_paginated.number > 2:
		previous_previous_page_number_exists = True
		previous_previous_page_number = post_list_paginated.previous_page_number() - 1

	if post_list_paginated.number < paginator.num_pages - 1:
		next_next_page_number_exists = True
		next_next_page_number = post_list_paginated.next_page_number() + 1

	return render(request, 'home.html', {
		'pagination_list': post_list_paginated,
		'previous_previous_page_number_exists': previous_previous_page_number_exists,
		'previous_previous_page_number': previous_previous_page_number,
		'next_next_page_number_exists': next_next_page_number_exists,
		'next_next_page_number': next_next_page_number
	})

@login_required
def add_post(request):
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.save()
			messages.success(request, 'Post Successful.')
			return redirect('imageboard:index')
	else:
		form = PostForm()

	return render(request, 'post/add.html', { 'form': form })

@login_required
def edit_post(request, post_id):
	p = get_object_or_404(Post, pk = post_id)

	if request.user.is_superuser is False:
		if request.user != p.user:
			messages.info(request, 'You do not own this object.')
			return redirect('imageboard:index')

	if request.method == 'POST':
		form = PostEditForm(request.POST, instance = p)
		form.save()
		messages.success(request, 'Post Successfully Edited.')

		return redirect('imageboard:index')

	else:
		form = PostEditForm(instance = p)

	return render(request, 'post/edit.html', { 'form': form })

@login_required
def delete_post(request, post_id):
	p = get_object_or_404(Post, pk = post_id)

	if request.user.is_superuser is False:
		if request.user != p.user:
			messages.info(request, 'You do not own this object.')
			return redirect('imageboard:index')

	p.delete()
	messages.success(request, 'Post Successfully Deleted.')

	return redirect('imageboard:index')

@login_required
def add_comment(request, post_id):
	if request.method == 'POST':
		form = CommentForm(request.POST, request.FILES)
		if form.is_valid():
			comment = form.save(commit=False)
			post = get_object_or_404(Post, pk = post_id)
			comment.post = post
			comment.user = request.user
			comment.save()
			messages.success(request, 'Comment Successful.')
			return redirect('imageboard:index')
	else:
		form = CommentForm()

	return render(request, 'comment/add.html', { 'form': form })

@login_required
def edit_comment(request, post_id, comment_id):
	c = get_object_or_404(Comment, pk = comment_id)

	if request.user.is_superuser is False:
		if request.user != c.user:
			messages.info(request, 'You do not own this object.')
			return redirect('imageboard:index')

	if request.method == 'POST':
		form = CommentEditForm(request.POST, instance = c)
		form.save()
		messages.success(request, 'Comment Successfully Edited.')

		return redirect('imageboard:index')

	else:
		form = PostEditForm(instance = c)

	return render(request, 'comment/edit.html', { 'form': form })

@login_required
def delete_comment(request, post_id, comment_id):
	c = get_object_or_404(Comment, pk = comment_id)

	if request.user.is_superuser is False:
		if request.user != c.user:
			messages.info(request, 'You do not own this object.')
			return redirect('imageboard:index')
	
	c.delete()
	messages.success(request, 'Comment Successfully Deleted.')

	return redirect('imageboard:index')

@login_required
def gallery(request):
	gallery_list = Post.objects.prefetch_related('comment_set').all().order_by('-id').exclude(image = '')
	paginator = Paginator(gallery_list, 40)

	page = request.GET.get('page')
	try:
		gallery_list_paginated = paginator.page(page)
	except PageNotAnInteger:
		gallery_list_paginated = paginator.page(1)
	except EmptyPage:
		gallery_list_paginated = paginator.page(paginator.num_pages)

	return render(request, 'gallery/home.html', { 'pagination_list': gallery_list_paginated })

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username = username, password = password)
		if user is not None:
			if user.is_active:
				login(request, user)
				messages.success(request, 'You were successfully logged in.')
				return redirect('imageboard:index')
			else:
				messages.error(request, 'Your account is currently disabled.')
		else:
			messages.error(request, 'Login failed, please check your credentials and try again.')

	return render(request, 'registration/login.html', { 'form': AuthenticationForm() })

def logout_view(request):
	logout(request)
	return redirect('imageboard:index')