from django.utils.functional import cached_property
from embed_video import backends

import json
import requests
import re


def match_protocol(protocol, url):
    """
    Ensures URL matches given request protocol

    Args:
        protocol: Requested protocol to be returned with url
        url: Valid URL string to be matched (begins with http:// or https://)

    Returns:
        URL string matching supplied protocol
    """
    re_protocol = re.compile(
        r'^(http://)',
        re.I
    )

    return re.sub(re_protocol, protocol + "://", url, count=1)


class YoutubeBackend(backends.YoutubeBackend):
    """
    Extends YoutubeBackend functionality for external embed_video library

    API Docs: https://developers.google.com/youtube/
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    base_url = '{protocol}://www.youtube.com/oembed'

    re_start = re.compile(
        r'''youtu((\.be)|(be\.com))/
            ([a-z0-9;:@?&%=+/\$_.-]+[&?])
            ((t|start)[=])
            ((?P<hours>\d+[h])?(?P<minutes>\d+[m])?(?P<seconds>\d+[s]?)?)''',
        re.I | re.X
    )

    @cached_property
    def info(self):
        """ Additional information about the embedded Youtube object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    @property
    def start(self):
        """
        Start time of video
        """
        return self.get_start_time()

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
        author = self.info.get('author_name')

        if author is None or author == '':
            return "Youtube"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the video title
        """
        title = self.info.get('title')

        if title is None or title == '':
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

    def get_start_time(self):
        """ Find video start time in url parameters

        Using format:: t/start = hours/minutes/seconds
        Otherwise returns 0 seconds if no matching time is given

        Returns:
            String representing video start in seconds
        """
        match = self.re_start.search(self._url)

        if match:
            time = {
                ('hours', 'h', 3600),
                ('minutes', 'm', 60),
                ('seconds', 's', 1)
            }
            start = 0
            for i in time:
                if match.group(i[0]) is not None or '':
                    start += int(match.group(i[0]).lower().split(i[1])[0]) * i[2]
            return str(start)
        else:
            return '0'


class VimeoBackend(backends.VimeoBackend):
    """
    Extends VimeoBackend functionality for external embed_video library

    API Docs: https://developer.vimeo.com/api
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_thumbnail_code = re.compile(
        r'''/(?P<code>[0-9]+)_''',
        re.I | re.X
    )

    base_url = '{protocol}://vimeo.com/api/oembed.json'
    pattern_thumbnail_url = '{protocol}://i.vimeocdn.com/video/{thumbnail_code}_{resolution}'
    resolutions = [
        '420x315.jpg', # Vimeo handles custom thumbnail sizes
        '640.jpg',
        '960.jpg',
        '1280.jpg',
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

    @property
    def start(self):
        """
        Start time of video
        """
        return self.get_start_time()

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
        author = self.info.get('author_name')

        if author is None or author == '':
            return "Vimeo"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the video title
        """
        title = self.info.get('title')

        if title is None or title == '':
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

    @staticmethod
    def get_start_time():
        """ Find video start time in url parameters

        Otherwise returns 0 seconds if no matching time is given

        Returns:
            String representing video start in seconds
        """
        return '0' # Not implemented by Vimeo


# TODO: Replace get_code and get_url to avoid making API call
# TODO: Fix broken playlist handling
class SoundCloudBackend(backends.SoundCloudBackend):
    """
    Extends SoundCloudBackend functionality for external embed_video library

    API Docs: https://developers.soundcloud.com/docs/api/reference
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

    @property
    def start(self):
        """
        Track start time
        """
        return self.get_start_time()

    def username(self):
        """
        Returns:
             String representing the artist name
        """
        author = self.info.get('author_name')

        if author is None or author == '':
            return "Soundcloud"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the track title
        """
        title = self.info.get('title')

        if title is None or title == '':
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

    @staticmethod
    def get_start_time():
        """ Find track start time in url parameters

        Otherwise returns 0 seconds if no matching time is given

        Returns:
            String representing track start in seconds
        """
        return '0' # Not handled by the SoundCloud embed player


class StreamableBackend(backends.VideoBackend):
    """
    StreamableBackend functionality for external embed_video library

    API Docs: https://streamable.com/documentation
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_detect = re.compile(
        r'''^(http(s)?://)?(www\.)?streamable\.com/([0-9a-zA-Z]*).*''',
        re.I | re.X
    )
    re_code = re.compile(
        r'''streamable\.com/(?P<code>[0-9a-zA-Z]+)''',
        re.I | re.X
    )
    re_start = re.compile(
        r'''streamable\.com/.+
            ([?&]t=)
            (?P<seconds>[\d]+(.\d)?)''',
        re.I | re.X
    )

    base_url = '{protocol}://api.streamable.com/oembed.json'
    pattern_url = '{protocol}://streamable.com/e/{code}'
    pattern_thumbnail_url = '{protocol}://cdn.streamable.com/image/{code}.jpg'

    @cached_property
    def info(self):
        """ Additional information about the embedded Streamable object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    @property
    def start(self):
        """
        Start time of video
        """
        return self.get_start_time()

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
        author = self.info.get('author_name')

        if author is None or author == '':
            return "Streamable"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the video title
        """
        title = self.info.get('title')

        if title is None or title == '':
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

    def get_start_time(self):
        """ Find video start time in url parameters

        Using format: t = seconds.hundredths
        Otherwise returns 0 seconds if no matching time is given

        Returns:
            String representing video start in seconds
        """
        match = self.re_start.search(self._url)

        if match:
            return match.group('seconds')
        else:
            return '0'


class DailymotionBackend(backends.VideoBackend):
    """
    DailymotionBackend functionality for external embed_video library

    API Docs: https://developer.dailymotion.com/player
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_detect = re.compile(
        r'''(^http(s)?://(www\.)?dailymotion\.com/video/)|
            (^http://dai\.ly/)
            ([a-zA-Z0-9]+).*''',
        re.I | re.X
    )
    re_code = re.compile(
        r'''(dailymotion\.com/video|dai\.ly)/
            (?P<code>[a-zA-Z0-9-]+).*''',
        re.I | re.X
    )
    re_thumbnail_code = re.compile(
        r'''/(?P<code>[a-zA-Z0-9]+)/''',
        re.I | re.X
    )
    re_start = re.compile(
        r'''(dailymotion\.com/video|dai\.ly)/.+
            ([?&]start=)
            (?P<seconds>[\d]+)''',
        re.I | re.X
    )

    base_url = '{protocol}://www.dailymotion.com/services/oembed'
    pattern_url = '{protocol}://www.dailymotion.com/embed/video/{code}'
    pattern_thumbnail_url = 'https://s1-ssl.dmcdn.net/{thumbnail_code}.jpg'

    @cached_property
    def info(self):
        """ Additional information about the embedded Dailymotion object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    @property
    def start(self):
        """
        Start time of video
        """
        return self.get_start_time()

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
        author = self.info.get('author_name')

        if author is None or author == '':
            return "Dailymotion"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the embed title
        """
        title = self.info.get('title')

        if title is None or title == '':
            return "Untitled"
        else:
            return self.info.get('title')

    def get_info(self):
        params = {
            'url': self._url,
            'maxwidth': self.EMBED_WIDTH_MAX,
            'maxheight': self.EMBED_WIDTH_MAX,
            'format': 'json'
        }
        r = requests.get(self.base_url.format(protocol=self.protocol),
                         params=params,
                         timeout=backends.EMBED_VIDEO_TIMEOUT)

        if r.status_code != 200:
            raise backends.VideoDoesntExistException(
                'Dailymotion returned status code `{0}`.'.format(r.status_code)
            )

        return json.loads(r.text)

    def get_thumbnail_url(self):
        thumbnail = self.info.get('thumbnail_url')

        if re.search(r'\.png$', thumbnail):
            return thumbnail

        code = self.re_thumbnail_code.search(thumbnail)
        if code:
            return self.pattern_thumbnail_url.format(
                protocol=self.protocol,
                thumbnail_code=code.group('code'))
        else:
            return thumbnail

    def get_start_time(self):
        """ Find video start time in url parameters

        Using format: start = seconds
        Otherwise returns 0 seconds if no matching time is given

        Returns:
            String representing video start in seconds
        """
        match = self.re_start.search(self._url)

        if match:
            return match.group('seconds')
        else:
            return '0'


class GfycatBackend(backends.VideoBackend):
    """
    GfycatBackend functionality for external embed_video library

    API Docs: https://gfycat.com/api
    """
    EMBED_WIDTH_MAX = 420
    EMBED_HEIGHT_MAX = 315

    re_detect = re.compile(
        r'''^(http(s)?://)?(www\.)?gfycat\.com/([a-zA-Z]*).*''',
        re.I | re.X
    )
    re_code = re.compile(
        r'''gfycat\.com/(detail/)?
            (?P<code>[a-zA-Z]+)''',
        re.I | re.X
    )

    base_url = '{protocol}://api.gfycat.com/v1/oembed'
    pattern_url = '{protocol}://www.gfycat.com/ifr/{code}'
    pattern_thumbnail_url = '{protocol}://thumbs.gfycat.com/{code}-poster.jpg'

    @cached_property
    def info(self):
        """ Additional information about the embedded Gfycat object

        Returned information is cached for the instance lifetime.

        Returns:
             String representing the parsed JSON information
        """
        return self.get_info()

    @property
    def start(self):
        """
        Start time of video
        """
        return self.get_start_time()

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
        author = self.info.get('author_name')

        if author is None or author == '':
            return "Gfycat"
        else:
            return self.info.get('author_name')

    def title(self):
        """
        Returns:
             String representing the embed title
        """
        title = self.info.get('title')

        if title is None or title == '':
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

    @staticmethod
    def get_start_time():
        """ Find video start time in url parameters

        Otherwise returns 0 seconds if no matching time is given

        Returns:
            String representing video start in seconds
        """
        return '0' # Not implemented by Gfycat
