from django.conf.urls import url

from . import views

app_name = 'imageboard'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^post/add/$', views.add_post, name='add_post'),
    url(r'^post/edit/(?P<post_id>\d+)/$', views.edit_post, name='edit_post'),
    url(r'^post/delete/(?P<post_id>\d+)/$', views.delete_post, name='delete_post'),
    url(r'^post/(?P<post_id>\d+)/comment/$', views.add_comment, name='add_comment'),
    url(r'^post/(?P<post_id>\d+)/comment/edit/(?P<comment_id>\d+)/$', views.edit_comment, name='edit_comment'),
    url(r'^post/(?P<post_id>\d+)/comment/delete/(?P<comment_id>\d+)/$', views.delete_comment, name='delete_comment'),
    url(r'^gallery/$', views.gallery, name='gallery'),
]