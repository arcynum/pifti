from django import template
from PIL import Image
from os.path import exists

register = template.Library()

@register.filter
def isgif(image):
    """
    Django template to check if image is an animated gif

    Returns:
        True if the filename ends with .gif and has frames
        Otherwise returns False
    """

    if not exists(image.path):
        return False

    image.open()
    gif = Image.open(image)
    try:
        gif.seek(1)
    except EOFError:
        return False
    else:
        return True
