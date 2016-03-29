from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from imageboard.forms import PostForm, PostEditForm, CommentForm, CommentEditForm, ProfileEditForm
from imageboard.models import Post, Comment, UserProfile
from math import ceil
from itertools import chain
from operator import attrgetter


@login_required
def index(request):
	post_list = Post.objects.prefetch_related('comment_set').order_by('-modified', '-id')
	profile, created = UserProfile.objects.get_or_create(id=request.user.id, user_id=request.user.id)
	
	paginator = Paginator(post_list, profile.pagination)

	page = request.GET.get('page')
	try:
		post_list_paginated = paginator.page(page)
	except PageNotAnInteger:
		post_list_paginated = paginator.page(1)
	except EmptyPage:
		post_list_paginated = paginator.page(paginator.num_pages)

	extras = _generateExtraPagination(paginator, post_list_paginated)
	activity = _getActivity(request)

	return render(request, 'home.html', {
		'pagination_list': post_list_paginated,
		'previous_previous_page_number_exists': extras['previous_previous_page_number_exists'],
		'previous_previous_page_number': extras['previous_previous_page_number'],
		'next_next_page_number_exists': extras['next_next_page_number_exists'],
		'next_next_page_number': extras['next_next_page_number'],
		'latest_activity': activity
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

		return redirect(reverse('imageboard:index')
						+ '?page=' + str(_getPostPage(post_id, request.user.id))
						+ '#' + post_id)

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

			return redirect(reverse('imageboard:index')
						+ '?page=' + str(_getPostPage(post_id, request.user.id))
						+ '#' + post_id)
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

		return redirect(reverse('imageboard:index')
						+ '?page=' + str(_getPostPage(post_id, request.user.id))
						+ '#' + post_id)

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

	return redirect(reverse('imageboard:index')
						+ '?page=' + str(_getPostPage(post_id, request.user.id))
						+ '#' + post_id)

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

	extras = _generateExtraPagination(paginator, gallery_list_paginated)

	return render(request, 'gallery/home.html', {
		'pagination_list': gallery_list_paginated,
		'previous_previous_page_number_exists': extras['previous_previous_page_number_exists'],
		'previous_previous_page_number': extras['previous_previous_page_number'],
		'next_next_page_number_exists': extras['next_next_page_number_exists'],
		'next_next_page_number': extras['next_next_page_number']
	})

@login_required
def profile(request):
	u = get_object_or_404(UserProfile, id=request.user.id)

	if request.method == 'POST':
		form = ProfileEditForm(request.POST, instance = u)
		form.save()
		messages.success(request, 'Profile Successfully Updated.')

		return redirect('imageboard:index')

	else:
		form = ProfileEditForm(instance = u)

	return render(request, 'profile/home.html', { 'form': form })

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

def _generateExtraPagination(paginator, page_list):
	# Adjusting the paginator rendering results for quicker paging.
	extras = {}

	extras['previous_previous_page_number_exists'] = False
	extras['next_next_page_number_exists'] = False
	extras['previous_previous_page_number'] = None
	extras['next_next_page_number'] = None

	if page_list.number > 2:
		extras['previous_previous_page_number_exists'] = True
		extras['previous_previous_page_number'] = page_list.previous_page_number() - 1

	if page_list.number < paginator.num_pages - 1:
		extras['next_next_page_number_exists'] = True
		extras['next_next_page_number'] = page_list.next_page_number() + 1

	return extras

def _getActivity(request):
	""" Retrieve the activity list

	List length is defined by the users activity_count

	Args:
	    request: sender request

	Returns:
	    A list of the latest posts and comments
	"""

	activity_count = UserProfile.objects.get(id=request.user.id).activity

	# Retrieve the latest posts and comments
	latest_posts = Post.objects.all().order_by('-id')[:activity_count]
	latest_comments = Comment.objects.all().order_by('-id')[:activity_count]

	# Sort both lists together, via latest date
	activity = sorted(chain(latest_posts, latest_comments), key=attrgetter('created'), reverse=True)[:activity_count]

	# Find the post page for each activity item
	for a in activity:
		if hasattr(a, 'post_id'): # Use parent post_id for comment
			post = a.post_id
		else: # Else use posts id
			post = a.id

		# Add post page number to activity item
		a.post_page = _getPostPage(post, request.user.id)

	return activity

def _getPostPage(post_id, user_id):
	""" Retrieve the page number for a post

	Args:
	    post_id: integer number of the post ID
	    user_id: integer number of the user ID

	Returns:
	    An integer representing the page number for a given post
	"""

	post_list = Post.objects.filter(modified__gte=Post.objects.get(id=post_id).modified)
	return ceil(post_list.count() / UserProfile.objects.get(id=user_id).pagination)