from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
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

	return render(request, 'home.html', {
		'pagination_list': post_list_paginated,
		'previous_previous_page_number_exists': extras['previous_previous_page_number_exists'],
		'previous_previous_page_number': extras['previous_previous_page_number'],
		'next_next_page_number_exists': extras['next_next_page_number_exists'],
		'next_next_page_number': extras['next_next_page_number'],
		'latest_activity': _getActivity(request)
	})

@login_required
def add_post(request):
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.save()

			_deleteActivity()  # Clear latest activity cache

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
			return redirect('imageboard:index', page=1)

	if request.method == 'POST':
		form = PostEditForm(request.POST, instance = p)
		form.save()
		messages.success(request, 'Post Successfully Edited.')

		return redirect(reverse('imageboard:index') +
						'?page=' +
						str(_getPostPage(post_id, request.user.userprofile.pagination)) +
						'#' + post_id)

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

	# Delete media template cache fragment and clear latest activity cache
	cache.delete(make_template_fragment_key('post_media', [post_id]))
	_deleteActivity()

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

			_deleteActivity()  # Clear latest activity cache

			messages.success(request, 'Comment Successful.')

			return redirect(reverse('imageboard:index') +
							'?page=' +
							str(_getPostPage(post_id, request.user.userprofile.pagination)) +
							'#' + post_id)
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

		return redirect(reverse('imageboard:index') +
						'?page=' +
						str(_getPostPage(post_id, request.user.userprofile.pagination)) +
						'#' + post_id)

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

	# Delete media template cache fragment and clear latest activity cache
	cache.delete(make_template_fragment_key('comment_media', [comment_id]))
	_deleteActivity()

	messages.success(request, 'Comment Successfully Deleted.')

	return redirect(reverse('imageboard:index') +
					'?page=' +
					str(_getPostPage(post_id, request.user.userprofile.pagination)) +
					'#' + post_id)

@login_required
def gallery(request):
	gallery_list = Post.objects.prefetch_related('comment_set').all().order_by('-modified', '-id').exclude(image = '')
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

def _generateActivity():
	"""	Generates and caches the lastest activity lists

	For a list of pagination options defined in the UserProfile model class
	the latest activity is generated and cached.

	Returns:
	    None
	"""

	# Find maximum activity list length
	ACTIVITY_MAX = max(UserProfile.ACTIVITY_CHOICES)[0] # [int, str]

	# Retrieve the latest posts and comments
	latest_posts = Post.objects.all().order_by('-id')[:ACTIVITY_MAX]
	latest_comments = Comment.objects.all().order_by('-id')[:ACTIVITY_MAX]

	# Sort both lists together, via latest date
	activity = sorted(chain(latest_posts, latest_comments),
					  key=attrgetter('created'), reverse=True)[:ACTIVITY_MAX]

	# For each pagination option create a latest activity list
	for p in UserProfile.PAGINATION_CHOICES: # [int, str]
		activity_key = 'activity_' + p[1]

		# Find and set the post page for each activity item
		for a in activity:
			if hasattr(a, 'post_id'):  # Use parent post_id for comments
				post = a.post_id
			else:  # Otherwise use the posts id
				post = a.id

			# Set post page number for activity item
			a.post_page = _getPostPage(post, p[0])

		cache.set(activity_key, activity)  # Cache latest activity

def _deleteActivity():
	"""	Clear the latest activity lists from cache

	Returns:
	    None
	"""

	for p in UserProfile.PAGINATION_CHOICES:
		cache.delete('activity_' + p[1])

def _getActivity(request):
	""" Retrieve the latest activity list

	Args:
	    request: sender request

	Returns:
	    A list of the latest posts and comments
	"""

	# Find appropriate cached activity list
	activity_key = 'activity_' + str(request.user.userprofile.pagination)
	activity = cache.get(activity_key)

	if activity is None:
		_generateActivity()
	activity = cache.get(activity_key)

	return activity[:request.user.userprofile.activity]

def _getPostPage(post_id, pagination):
	""" Find the page number for a specific post

	Args:
	    post_id: integer representing the internal post ID
	    pagination: integer representing the user's post count profile option

	Returns:
	    An integer representing the page number for a given post and pagination
	"""

	post_list = Post.objects.filter(modified__gte=Post.objects.get(id=post_id).modified)
	return ceil(post_list.count() / pagination)