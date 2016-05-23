from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe, SafeData
from django.utils.html import escape
from emojipy import Emoji
from os.path import exists
import imageio

register = template.Library()


# Template Filters

@register.filter(name='isanimated')
def is_animated(image):
    """
    Checks if the supplied image is an animated gif

    Args:
        image: A ThumbnailerImageField instance

    Returns:
        True if the file type is GIF and has multiple frames
        False otherwise

    Sample Usage::

        {% if model.image|isanimated %}
    """
    # Ensure file exists
    if not exists(image.path):
        return False

    # Open ThumbnailerExtField for reading
    image.open()

    # Formats for animated images/videos
    animated_formats = {
        'GIF': 'GIF',
        'FFMPEG': 'VIDEO',
    }

    try:
        image = imageio.get_reader(image.path)
        if image.format.name in animated_formats.keys():
            # Check if GIF has multiple frames
            if image.format.name == 'GIF':
                try:
                    image.get_data(1)
                except ValueError:
                    # GIF only has one frame
                    return False
            return True
        else:
            return False
    except ValueError:
        # No reader or format, fail silently
        return False

@register.filter(name='emojize', is_safe=True, needs_autoescape=True)
@stringfilter
def emoji_replace(text, autoescape=True):
    """
    Replaces Unicode and Shortcode emoji's with embedded images,
    using the Emojipy library

    Args:
        text: A string to be matched for shortcode and unicode emojis
        autoescape: Optional argument for autoescaping of input string before processing

    Returns:
        Safe text
    """
    # Escape text if it is not safe
    autoescape = autoescape and not isinstance(text, SafeData)
    if autoescape:
        text = escape(text)

    text = Emoji.unicode_to_image(text)
    text = Emoji.shortcode_to_image(text)

    return mark_safe(text)


# Template Tags

@register.simple_tag(name='imagetype')
def image_type_tag(image):
    """
    Prints the image format extension

    Args:
        image: A ThumbnailerImageField instance

    Returns:
         A string representation of the image file type
         e.g. PNG, JPEG, GIF

    Sample Usage::

        {% imagetype model.image %}
    """
    # Ensure file exists
    if not exists(image.path):
        return ''

    # Open ThumbnailerExtField for reading
    image.open()

    formats = {
        'JPEG': 'JPG',
        'PNG': 'PNG',
        'GIF': 'GIF',
        'ICO': 'ICO',
        'FFMPEG': 'VIDEO',
    }

    try:
        image = imageio.get_reader(image.path)
        if image.format.name in formats.keys():
            return formats[image.format.name]
    except ValueError:
        # No reader or format, fail silently
        return ''
