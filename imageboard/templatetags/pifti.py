from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe, SafeData
from django.utils.html import escape
from PIL import Image
from emojipy import Emoji
from os.path import exists

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

    if not exists(image.path):
        return False

    image.open()
    image = Image.open(image)

    if image.format == 'GIF':
        try:
            image.seek(1)
        except EOFError:
            return False
        else:
           return True
    else:
        return False

@register.filter(name='emojize', is_safe=True, needs_autoescape=True)
@stringfilter
def emoji_replace(text, autoescape=True):
    """
    Replaces Unicode and Shortcode emoji's with embedded images,
    using the Emojipy library

    Args:
        text: A string to be matched for shortcode and unicode emojis

    Returns:
        Safe text
    """

    autoescape = autoescape and not isinstance(text, SafeData)
    if autoescape:
        text = escape(text)

    text = Emoji.shortcode_to_image(text)
    text = Emoji.unicode_to_image(text)
    #text = Emoji.ascii_to_image(text)

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

    if not exists(image.path):
        return ''

    image.open()
    image = Image.open(image)

    return image.format
