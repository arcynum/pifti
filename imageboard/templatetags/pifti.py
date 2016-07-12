from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe, SafeData
from django.utils.html import escape
from imageboard.models import Post
from math import ceil
from emojipy import Emoji

register = template.Library()


# Template Filters

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

@register.filter(name='excludedbackend')
def is_excluded_backend(backend):
    """
    Checks if a given backend is in the list of excluded backends.

    Args:
        backend: String representing the backend name, e.g. 'YoutubeBackend'
    Returns:
        True if the backend is excluded
        False otherwise
    Sample Usage::
        {% if model.backend|excludedbackend %}
    """
    from imageboard.conf import IMAGEBOARD_SERVER_EMBEDS as excluded

    if backend in excluded:
        return True
    else:
        return False


# Template Tags

@register.simple_tag(name='posturl')
def post_link(post_id, pagination):
    """ Get the url link to a post

    Args:
        post_id: integer representing the internal post ID
        pagination: integer representing a pagination option

    Returns:
        Url to post page with anchor
    """

    post_count = Post.objects.filter(modified__gte=Post.objects.get(id=post_id).modified).count()
    post_page = ceil(post_count / pagination)
    index = reverse('imageboard:index')

    return index + '?page=' + str(post_page) + '#' + str(post_id)
