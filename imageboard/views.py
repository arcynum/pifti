from django.shortcuts import render_to_response, get_object_or_404
from imageboard.models import Post, Comment

def index(request):
  post_list = Post.objects.all()
  return render_to_response('home.html', {'post_list': post_list})
  
def view_post(request, post_id):
  p = get_object_or_404(Post, pk = post_id)
  return render_to_response('post/view.html', {'post': p})
