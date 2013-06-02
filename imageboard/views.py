from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from imageboard.models import Post, Comment
from django.core.urlresolvers import reverse

from imageboard.forms import PostForm

def index(request):
  post_list = Post.objects.all()
  return render(request, 'home.html', {'post_list': post_list})
  
def view_post(request, post_id):
  p = get_object_or_404(Post, pk = post_id)
  return render(request, 'post/view.html', { 'post': p })

def add_post(request):
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = Post()
			post.title = form.cleaned_data['title']
			post.body = form.cleaned_data['body']
			post.user = request.user
			post.image = request.FILES['image']
			post.save()
			return HttpResponseRedirect(reverse('index'))
	else:
		form = PostForm()

	return render(request, 'post/add.html', { 'form': form })