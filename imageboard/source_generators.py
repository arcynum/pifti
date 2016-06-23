from easy_thumbnails import utils
from imageboard.utils import force_close_reader
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
    reader = None

    try:
        # Get imageio reader
        reader = imageio.get_reader(source.path)

        # Send data to PIL
        image = Image.fromarray(reader.get_data(0))

        # Reorient the image
        if exif_orientation:
            image = utils.exif_orientation(image)

        return image
    except ValueError:
        # Fail Loudly
        raise Exception
    except OSError:
        # Out of memory for a new reader (bug #48)
        raise Exception
    finally:
        # Make sure any open reader is closed
        force_close_reader(reader)
