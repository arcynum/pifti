from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'imageboard.views.index'),
    url(r'^post/(?P<post_id>\d+)/$', 'imageboard.views.view_post'),
    # url(r'^ifti/', include('ifti.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
)
