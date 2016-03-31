from django import template
from PIL import Image

register = template.Library()

@register.filter
def isgif(image):
    """
    Django template to check if image is an animated gif

    Returns:
        True if the filename ends with .gif and has frames
        Otherwise returns False
    """

    if image.name.endswith('.gif'):
        gif = Image.open(image)
        try:
            gif.seek(1)
        except EOFError:
            return False
        else:
            return True
    else:
        return False
