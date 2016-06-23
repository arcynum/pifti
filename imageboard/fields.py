from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerField
from imageboard.files import ThumbnailerImageExtFieldFile, ImageExtField
from imageboard.conf import IMAGEBOARD_FORMATS as formats
from imageboard.utils import force_close_reader

from io import BytesIO
from tempfile import NamedTemporaryFile


class ThumbnailerExtField(ThumbnailerField, ImageExtField):
    """
    Extends the easy-thumbnail ThumbnailerField to add restricted support
    for images/video provided by the FreeImage and FFmpeg imageio plugins.
    """
    types = "JPG, PNG, GIF, ICO, WEBM, MP4"
    default_error_messages = {
        'invalid_file': _("Invalid file, supported files: %(types)s."),
        'invalid_extension': _("File has no valid extension."),
        'max_size': _("This file is too large (5MB Limit)."),
        'unsupported': _("This format is unsupported,"
                         " supported formats are: %(types)s."),
        'corrupt_file': _("%(file)s is corrupt."),
    }

    attr_class = ThumbnailerImageExtFieldFile

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid source file
        (GIF, JPG, PNG, WEBM, MP4, etc) using imageio plugins.
        """
        f = super(ThumbnailerExtField, self).to_python(data)
        if f is None:
            return None

        # Check filesize limit
        # Nginx client_max_body_size is 5MB
        if f.size > 5 * 1024 * 1024:
            raise ValidationError(self.error_messages['max_size'],
                                  code='max_size')

        from pathlib import PurePath

        # Check for file extension
        ext = PurePath(f.name).suffix
        if ext == '':
            raise ValidationError(self.error_messages['invalid_extension'],
                                  code='invalid_extension')

        # Get temporary file path or raw bytes
        if hasattr(data, 'temporary_file_path'):
            file = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                file = BytesIO(data.read())
            else:
                file = BytesIO(data['content'])

        from PIL import Image
        from imageio import get_reader

        try:
            # Firstly try and recognise BytesIO
            file = get_reader(file)
            # Send data to PIL
            f.image = Image.fromarray(file.get_data(0))
            # Close the reader
            force_close_reader(file)
        except ValueError:
            # Create a local file
            with NamedTemporaryFile(suffix=ext) as n:
                for chunk in data.chunks():
                    n.write(chunk)
                try:
                    # Try and read from temporary file
                    file = get_reader(n.name)
                    # Send data to PIL
                    f.image = Image.fromarray(file.get_data(0))
                except OSError:
                    # FFmpeg cannot read video meta
                    # May be out of memory for a new reader (bug #48)
                    params = { 'file': f.name }
                    raise ValidationError(self.error_messages['corrupt_file'],
                                          code='corrupt_file',
                                          params=params)
                except Exception:
                    # imageio doesn't recognize it as an image.
                    params = { 'types': self.types }
                    raise ValidationError(self.error_messages['invalid_file'],
                                          code='invalid_file',
                                          params=params)
                finally:
                    # Close Named Tempoary File
                    n.close()
                    # Make sure any open reader is closed
                    force_close_reader(file)

        # Check if this format is enabled
        # See ``imageboard.settings`` for more information
        if file.format.name in formats.keys():
            # MIME type is not supported with imageio
            # Thus if the content type is not detected, it will remain as None
            f.content_type = Image.MIME.get(f.image.format)

            if hasattr(f, 'seek') and callable(f.seek):
                f.seek(0)

            return f
        else:
            params = { 'types': self.types }
            raise ValidationError(self.error_messages['unsupported'],
                                  code='unsupported',
                                  params=params)
