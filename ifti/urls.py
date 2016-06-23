"""
Pifti URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from imageio import formats
from imageio.plugins.ffmpeg import FfmpegFormat
from imageio.plugins.avbin import AvBinFormat


urlpatterns = [
    url(r'', include('imageboard.urls')),
    url(r'^admin/', admin.site.urls)
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# TODO: Clean up
avbin = AvBinFormat('avbin', 'Many video formats (via avbin)',
                    '', 'I')
ffmpeg = FfmpegFormat('ffmpeg', 'Many video formats and cameras (via ffmpeg)',
                      'mp4 webm', 'I')
# Register imageio formats
formats.add_format(avbin, overwrite=True)
formats.add_format(ffmpeg, overwrite=True)


# The additional section with the static method needs to be removed in production.
# The static and media files will be hosted on a traditional web server, not through python.
