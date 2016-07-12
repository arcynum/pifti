from django.conf import settings


IMAGEBOARD_FORMATS = getattr(settings, 'IMAGEBOARD_FORMATS',
    {
        'JPEG': {'code': 'JPG', 'animated': False},
        'PNG': {'code': 'PNG', 'animated': False},
        'ICO': {'code': 'ICO', 'animated': False},
        'GIF': {'code': 'GIF', 'animated': True},
        'FFMPEG': {'code': 'VIDEO', 'animated': True},
    }
)
"""
The default formats which Pifti will handle. All replacements must be supplied
with `code` and `animated` fields, and must be supported by the imageio library.
Imageio formats: https://imageio.readthedocs.io/en/latest/formats.html

Overwrite this in your application settings to alter format support.
"""

IMAGEBOARD_SERVER_EMBEDS = getattr(settings, 'IMAGEBOARD_SERVER_EMBEDS',
     {
         'YoutubeBackend',
         'DailymotionBackend'
     }
 )
"""
The default embeds which Pifti will force the loading of responsive embed data
from via its embed_video backend.

Requesting data through the server backend is a slow process because it is
generated synchronously when building the template context. However loading data
through the client browser is forbidden for some backends, such as Youtube's
oEmbed API which blocks cross-domain requests. Thus this setting is configured
for those backends by default.

Overwrite this in your application settings to force loading of the listed
backends through the server, rather than client side javascript.
"""
