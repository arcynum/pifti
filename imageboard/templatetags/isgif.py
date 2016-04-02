from django import template
from PIL import Image
from os.path import exists

register = template.Library()

@register.filter(name="isgif")
def isgif(image):
    """
    Django template to check if image is an animated gif

    Returns:
        True if the file type is GIF and has frames
        Otherwise returns False
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
