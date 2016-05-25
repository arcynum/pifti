from django.utils.functional import cached_property
from embed_video import backends

import json
import requests
import re


def match_protocol(protocol, url):
    """
    Ensures URL protocol matches request protocol

    Args:
        protocol: Request protocol string, e.g. 'http', 'https'
        url: URL string

    Returns:
        URL string
    """
    re_protocol = re.compile(
        r'^(http://)',
        re.I
    )

    return re.sub(re_protocol, protocol + "://", url, count=1)


class YoutubeBackend(backends.YoutubeBackend):
    """
    Extends YoutubeBackend functionality for external embed_video library
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    base_url = '{protocol}://www.youtube.com/oembed'

    @cached_property
    def info(self):
        """ Additional information about the embedded Youtube object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    def width(self):
        """
        Returns:
             String representing the embeded player width in pixels
        """
        return self.info.get('width')

    def height(self):
        """
        Returns:
             String representing the embeded player height in pixels
        """
        return self.info.get('height')

    def username(self):
        """
        Returns:
             String representing the channel name
        """
        if self.info.get('author_name') is None:
            return "Anonymous"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the video title
        """
        if self.info.get('title') is None:
            return "Untitled"
        else:
            return self.info.get('title')

    def get_info(self):
        params = {
            'url': self._url,
            'maxwidth': self.EMBED_WIDTH_MAX,
            'maxheight': self.EMBED_HEIGHT_MAX,
            'format': 'json'
        }
        r = requests.get(self.base_url.format(protocol=self.protocol),
                         params=params,
                         timeout=backends.EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise backends.VideoDoesntExistException(
                'Youtube returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)


class VimeoBackend(backends.VimeoBackend):
    """
    Extends VimeoBackend functionality for external embed_video library
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_thumbnail_code = re.compile(
        r'/(?P<code>[0-9]+)_',
        re.I | re.X
    )

    base_url = '{protocol}://vimeo.com/api/oembed.json'
    pattern_thumbnail_url = '{protocol}://i.vimeocdn.com/video/{thumbnail_code}_{resolution}'
    resolutions = [
        '1280.jpg',
        '960.jpg',
        '640.jpg',
        '295x166.jpg',
        '100x75.jpg',
    ]

    @cached_property
    def info(self):
        """ Additional information about the embedded Vimeo object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    def width(self):
        """
        Returns:
             String representing the embeded player width in pixels
        """
        return self.info.get('width')

    def height(self):
        """
        Returns:
             String representing the embeded player height in pixels
        """
        return self.info.get('height')

    def username(self):
        """
        Returns:
             String representing the channel name
        """
        if self.info.get('author_name') is None:
            return "Anonymous"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the video title
        """
        if self.info.get('title') is None:
            return "Untitled"
        else:
            return self.info.get('title')

    def get_info(self):
        params = {
            'url': self._url,
            'maxwidth': self.EMBED_WIDTH_MAX,
            'maxheight': self.EMBED_WIDTH_MAX
        }
        r = requests.get(self.base_url.format(protocol=self.protocol),
                         params=params,
                         timeout=backends.EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise backends.VideoDoesntExistException(
                'Vimeo returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)

    def get_thumbnail_url(self):
        """
        Returns thumbnail URL folded from :py:data:`pattern_thumbnail_url` and
        parsed thumbnail code

        :rtype: str
        """
        thumbnail = self.info.get('thumbnail_url')

        code = self.re_thumbnail_code.search(thumbnail)
        if code:
            for resolution in self.resolutions:
                temp_thumbnail_url = self.pattern_thumbnail_url.format(
                    protocol=self.protocol,
                    thumbnail_code=code.group('code'),
                    resolution=resolution)
                if int(requests.head(temp_thumbnail_url).status_code) < 400:
                    return temp_thumbnail_url

        return thumbnail


class SoundCloudBackend(backends.SoundCloudBackend):
    """
    Extends SoundCloudBackend functionality for external embed_video library
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 176

    base_url = '{protocol}://soundcloud.com/oembed'

    @cached_property
    def info(self):
        """ Additional information about the embedded SoundCloud object

        Returned request information is cached for the instance lifetime

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    def username(self):
        """
        Returns:
             String representing the artist name
        """
        if self.info.get('author_name') is None:
            return "Anonymous"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the track title
        """
        if self.info.get('title') is None:
            return "Untitled"
        else:
            return self.info.get('title')

    def get_info(self):
        params = {
            'url': self._url,
            'maxwidth': self.EMBED_WIDTH_MAX,
            'maxheight': self.EMBED_HEIGHT_MAX,
            'format': 'json'
        }
        r = requests.get(self.base_url.format(protocol=self.protocol),
                         params=params,
                         timeout=backends.EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise backends.VideoDoesntExistException(
                'SoundCloud returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)

    def get_thumbnail_url(self):
        """
        Returns a string representing the soundcloud thumbnail url

        Returns:
            Thumbnail url
        """
        return match_protocol(self.protocol, self.info.get('thumbnail_url'))


class StreamableBackend(backends.VideoBackend):
    """
    StreamableBackend functionality for external embed_video library
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_detect = re.compile(
        r'^((http(s)?:)?//)?(www\.)?streamable\.com/([0-9a-zA-Z]*)$', re.I
    )
    re_code = re.compile(r'''streamable\.com/(?P<code>[0-9a-zA-Z]+)''', re.I)

    base_url = '{protocol}://api.streamable.com/oembed.json'
    pattern_thumbnail_url = '{protocol}://cdn.streamable.com/image/{code}.jpg'

    @cached_property
    def info(self):
        """ Additional information about the embedded Streamable object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    def width(self):
        """
        Returns:
             String representing the embeded player width in pixels
        """
        return self.info.get('width')

    def height(self):
        """
        Returns:
             String representing the embeded player height in pixels
        """
        return self.info.get('height')

    def username(self):
        """
        Returns:
             String representing the channel name
        """
        if self.info.get('author_name') is None:
            return "Streamable"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the video title
        """
        if self.info.get('title') is None:
            return "Untitled"
        else:
            return self.info.get('title')

    def get_info(self):
        params = {
            'url': self._url,
            'maxwidth': self.EMBED_WIDTH_MAX,
            'maxheight': self.EMBED_WIDTH_MAX
        }
        r = requests.get(self.base_url.format(protocol=self.protocol),
                         params=params,
                         timeout=backends.EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise backends.VideoDoesntExistException(
                'Streamable returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)

    def get_thumbnail_url(self):
        return self.pattern_thumbnail_url.format(protocol=self.protocol,
                                                 code=self.code)

class GfycatBackend(backends.VideoBackend):
    """
    GfycatBackend functionality for external embed_video library
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_detect = re.compile(
        r'^((http(s)?:)?//)?(www\.)?gfycat\.com/([a-zA-Z]*)$', re.I
    )
    re_code = re.compile(r'''gfycat\.com/(detail/)?(?P<code>[a-zA-Z]+)''', re.I)

    base_url = '{protocol}://api.gfycat.com/v1/oembed'
    pattern_thumbnail_url = '{protocol}://thumbs.gfycat.com/{code}-poster.jpg'

    @cached_property
    def info(self):
        """ Additional information about the embedded Gfycat object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    def width(self):
        """
        Returns:
             String representing the embeded player width in pixels
        """
        return self.info.get('width')

    def height(self):
        """
        Returns:
             String representing the embeded player height in pixels
        """
        return self.info.get('height')

    def username(self):
        """
        Returns:
             String representing the author name
        """
        if self.info.get('author_name') is None:
            return "Gfycat"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the embed title
        """
        if self.info.get('title') is None:
            return "Untitled"
        else:
            return self.info.get('title')

    def get_info(self):
        params = {
            'url': self._url,
            'maxwidth': self.EMBED_WIDTH_MAX,
            'maxheight': self.EMBED_WIDTH_MAX
        }
        r = requests.get(self.base_url.format(protocol=self.protocol),
                         params=params,
                         timeout=backends.EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise backends.VideoDoesntExistException(
                'Gfycat returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)

    def get_thumbnail_url(self):
        return self.pattern_thumbnail_url.format(protocol=self.protocol,
                                                 code=self.code)
