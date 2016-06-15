from easy_thumbnails import utils
from PIL import Image
import imageio


def video_image(source, exif_orientation=True, **options):
    """
    Try to find an imageio reader for the source and hand off the data
    to PIL for processing.

    source:
        ThumbnailerExtField instance
    exif_orientation:
        If EXIF orientation data is present, perform any required reorientation
        before passing the data along the processing pipeline.

    """
    try:
        # Get imageio reader
        image = imageio.get_reader(source.path)

        # Send data to PIL
        image = Image.fromarray(image.get_data(0))

        # Reorient the image
        if exif_orientation:
            image = utils.exif_orientation(image)

        return image
    except ValueError:
        # Fail silently
        raise Exception
    except OSError:
        # Fail loudly
        raise Exception
