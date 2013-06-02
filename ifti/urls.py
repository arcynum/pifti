from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'imageboard.views.index', name='index'),
    url(r'^post/(?P<post_id>\d+)/$', 'imageboard.views.view_post', name='view_post'),
    url(r'^post/add/', 'imageboard.views.add_post', name='add_post'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
)


# User for serving local files while in debug mode.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))