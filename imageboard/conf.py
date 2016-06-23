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

Overwrite this in your application settings to alter format support.
Imageio formats: https://imageio.readthedocs.io/en/latest/formats.html
"""
