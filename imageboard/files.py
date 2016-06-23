from django.apps import apps
from django.core import checks
from django.core.files import File
from django.db.models import signals
from django.db.models.fields.files import FieldFile, FileField, FileDescriptor
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.files import ThumbnailerFieldFile



def database_get_image_attributes(file, close=False):
    """
    Returns both the animated and format attributes for an ImageExtFile.
    Set `close` to True if `file` is a file object, to ensure it is closed.
    Otherwise the file will be accessed directly at the supplied path.

    Adds attributes to the database from file if they do not already exist.
    """
    SourceAttributes = apps.get_model('imageboard', 'SourceAttributes')

    try:
        attributes_cache = SourceAttributes.objects.get(
            name=file.name.lstrip('./'))
    except SourceAttributes.DoesNotExist:
        attributes_cache = None

    if attributes_cache:
        return attributes_cache.animated, attributes_cache.format
    else:
        attributes = get_image_attributes(file, close=close)

    if attributes_cache is None:
        # Return or create a new entry
        SourceAttributes.objects.get_or_create(
            name=file.name.lstrip('./'),
            defaults={'animated': attributes[0], 'format': attributes[1]})

    return attributes

def database_update_image_attributes(file, close=False):
    """
    Updates both the animated and format attributes for an ImageExtFile.
    Set `close` to True if `file` is a file object, to ensure it is closed.
    Otherwise the file will be accessed directly at the supplied path.

    Adds attributes to the database from file if they do not already exist.
    """
    attributes = get_image_attributes(file, close=close)

    SourceAttributes = apps.get_model('imageboard', 'SourceAttributes')
    SourceAttributes.objects.update_or_create(
        name=file.name.lstrip('./'),
        defaults={'animated': attributes[0], 'format': attributes[1]})

def database_delete_image_attributes(file):
    """
    Deletes the animated and format attributes for an ImageExtFile.
    """
    SourceAttributes = apps.get_model('imageboard', 'SourceAttributes')
    SourceAttributes.objects.filter(name=file.name.lstrip('./')).delete()

def get_image_attributes(file_or_path, close=False):
    """
    Returns a tuple with the animated(boolean) and format(str) of an image.
    Firstly the file will be accessed directly at a supplied path. Otherwise
    set `close` to True if `file_or_path` is a file to ensure it is closed.

    If there is an error when accessing the file or `IMAGEBOARD_FORMATS` is not
    configured correctly the defaults will be returned (False, None).
    """
    from imageboard.conf import IMAGEBOARD_FORMATS as formats
    from imageboard.utils import force_close_reader
    from imageio import get_reader
    from os.path import exists

    _animated = False
    _format = None
    f = None

    if hasattr(file_or_path, 'path'):
        if not exists(file_or_path.path):
            # No file at path. Should raise an error here but we will return
            # defaults instead.
            return _animated, _format
        file = file_or_path.path
        close = False
    elif hasattr(file_or_path, 'read'):
        file = file_or_path
        if not exists(file):
            # No file at path. Should raise an error here but we will return
            # defaults instead.
            return _animated, _format
        file.open()
        file.seek(0)
    else:
        raise AttributeError("No file or path given.")

    try:
        f = get_reader(file)
        try:
            _format = formats[f.format.name]['code']
            _animated = formats[f.format.name]['animated']
        except KeyError:
            # Format type or animated not in formats. See `imageboard.conf` for
            # information on how to configure the IMAGEBOARD_FORMATS setting
            # to support formats correctly.
            raise ValueError

        # Check if GIF has multiple frames. Extra support is required for other
        # formats with either single or multiple frames.
        # Request support here: https://github.com/arcynum/pifti/issues
        if _animated and _format == 'GIF':
            try:
                f.get_data(1)
            except ValueError:
                # GIF only has one frame, is not animated
                _animated = False
    except ValueError:
        # No reader or format, fail silently
        pass
    except OSError:
        # Out of memory for a new reader (bug #48)
        pass
    finally:
        # Close the file
        if close:
            file.close()
        # Close the reader
        force_close_reader(f)

    return _animated, _format


class ImageExtFile(File):
    """
    A mixin for use alongside django.core.files.base.File, which provides
    additional features for dealing with images.
    """
    def _get_animated(self):
        return self._get_image_attributes()[0]

    animated = property(_get_animated)

    def _get_format(self):
        return self._get_image_attributes()[1]

    format = property(_get_format)

    def _get_image_attributes(self):
        if not hasattr(self, '_attributes_cache'):
            close = self.closed
            self._attributes_cache = database_get_image_attributes(
                self,
                close=close)
        return self._attributes_cache

    def set_image_attributes(self):
        close = self.closed
        database_update_image_attributes(self, close=close)

    set_image_attributes.alters_data = True


class ImageExtFileDescriptor(FileDescriptor):
    """
    Just like the FileDescriptor, but for ImageFields. The only difference is
    assigning the width/height to the width_field/height_field, if appropriate.
    """
    def __set__(self, instance, value):
        previous_file = instance.__dict__.get(self.field.name)
        super(ImageExtFileDescriptor, self).__set__(instance, value)

        # To prevent recalculating image dimensions when we are instantiating
        # an object from the database (bug #11084), only update dimensions if
        # the field had a value before this assignment.  Since the default
        # value for FileField subclasses is an instance of field.attr_class,
        # previous_file will only be None when we are called from
        # Model.__init__().  The ImageExtField.update_attribute_fields method
        # hooked up to the post_init signal handles the Model.__init__() cases.
        # Assignment happening outside of Model.__init__() will trigger the
        # update right here.
        if previous_file is not None:
            self.field.update_attribute_fields(instance, force=True)


class ImageExtFieldFile(ImageExtFile, FieldFile):
    def delete(self, *args, **kwargs):
        """
        Delete the image attribute cache.
        """
        # Clear the image attributes cache
        if hasattr(self, '_attributes_cache'):
            del self._attributes_cache
        # Delete database entry
        database_delete_image_attributes(self)

    delete.alters_data = True


class ImageExtField(FileField):
    attr_class = ImageExtFieldFile
    descriptor_class = ImageExtFileDescriptor
    description = _("Image and Video")

    def __init__(self, verbose_name=None, name=None, animated_field=None,
            format_field=None, **kwargs):
        self.animated_field, self.format_field = animated_field, format_field
        super(ImageExtField, self).__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        errors = super(ImageExtField, self).check(**kwargs)
        errors.extend(self._check_image_library_installed())
        return errors

    def _check_image_library_installed(self):
        """
        Attempts to import imageio to ensure the library is installed properly.

        Currently there is no provided alternative library on import error.
        """
        try:
            import imageio # NOQA
        except ImportError:
            return [
                checks.Error(
                    'Cannot use ImageExtField because imageio is not installed.',
                    hint=('Get imageio at: https://imageio.github.io/ '
                          'or run command "pip install imageio".'),
                    obj=self,
                    id='fields.E210',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super(ImageExtField, self).deconstruct()
        if self.animated_field:
            kwargs['animated_field'] = self.animated_field
        if self.format_field:
            kwargs['format_field'] = self.format_field
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super(ImageExtField, self).contribute_to_class(cls, name, **kwargs)
        # Attach update_attribute_fields so that attribute fields declared
        # after their corresponding image field don't stay cleared by
        # Model.__init__, (bug #11196).
        # Only run post-initialization attribute update on non-abstract models
        if not cls._meta.abstract:
            signals.post_init.connect(self.update_attribute_fields, sender=cls)

    def update_attribute_fields(self, instance, force=False, *args, **kwargs):
        """
        Updates field's animated and format fields, if they are defined.

        This method is connected to the model's post_init signal to update
        attributes after instantiating a model instance. However, attributes
        won't be updated if the fields are already populated. This avoids
        unnecessary recalculation when loading an object from the database.

        Attributes can be forced to update with force=True, which is how
        ImageExtFileDescriptor.__set__ calls this method.
        """
        # Nothing to update if the field doesn't have attribute fields.
        has_attribute_fields = self.animated_field or self.format_field
        if not has_attribute_fields:
            return

        # getattr will call the FileDescriptor's __get__ method, which
        # coerces the assigned value into an instance of self.attr_class
        # (ImageExtFieldFile in this case).
        file = getattr(instance, self.attname)

        # Nothing to update with no file and not being forced to update.
        if not file and not force:
            return

        attribute_fields_filled = not(
            (self.animated_field and not getattr(instance, self.animated_field))
            or (self.format_field and not getattr(instance, self.format_field))
        )
        # When both attribute fields have values, we are most likely loading
        # data from the database or updating an image field that already had
        # an image stored.  In the first case, we don't want to update the
        # attribute fields because we are already getting their values from the
        # database.  In the second case, we do want to update the attributes
        # fields and will skip this return because force will be True since we
        # were called from ImageExtFileDescriptor.__set__.
        if attribute_fields_filled and not force:
            return

        # file should be an instance of ImageExtFieldFile or should be None.
        if file:
            animated = file.animated
            format = file.format
        else:
            # No file, so clear attributes fields.
            animated = False
            format = None

        # Update the animated and format fields.
        if self.animated_field:
            setattr(instance, self.animated_field, animated)
        if self.format_field:
            setattr(instance, self.format_field, format)


class ThumbnailerImageExtFieldFile(ImageExtFieldFile, ThumbnailerFieldFile):
    """
    Metaclass for ThumbnailerExtField which extends easy_thumbnails to add
    methods for generating and returning source image attributes.
    """

    def delete(self, *args, **kwargs):
        """
        Delete the image attributes, sources, and thumbnails.
        """
        ImageExtFieldFile.delete(self, *args, **kwargs)
        ThumbnailerFieldFile.delete(self, *args, **kwargs)

    delete.alters_data = True
