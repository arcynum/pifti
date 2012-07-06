from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'imageboard.views.index'),
    # url(r'^ifti/', include('ifti.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login'),

)
