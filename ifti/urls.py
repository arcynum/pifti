from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'imageboard.views.index', name='index'),
    url(r'^post/add/$', 'imageboard.views.add_post', name='add_post'),
    url(r'^post/edit/(?P<post_id>\d+)/$', 'imageboard.views.edit_post', name='edit_post'),
    url(r'^post/delete/(?P<post_id>\d+)/$', 'imageboard.views.delete_post', name='delete_post'),
    url(r'^post/(?P<post_id>\d+)/comment/$', 'imageboard.views.add_comment', name='add_comment'),
    url(r'^post/(?P<post_id>\d+)/comment/edit/(?P<comment_id>\d+)/$', 'imageboard.views.edit_comment', name='edit_comment'),
    url(r'^post/(?P<post_id>\d+)/comment/delete/(?P<comment_id>\d+)/$', 'imageboard.views.delete_comment', name='delete_comment'),
    url(r'^gallery/$', 'imageboard.views.gallery', name='gallery'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'imageboard.views.logout_view', name='logout'),
)

# url(r'^post/(?P<post_id>\d+)/$', 'imageboard.views.view_post', name='view_post'),

# User for serving local files while in debug mode.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
    urlpatterns += staticfiles_urlpatterns()