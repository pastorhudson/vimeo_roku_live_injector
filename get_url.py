import youtube_dl
import os
import requests
from datetime import datetime, timedelta
from pytz import timezone
from pytz.reference import Eastern


def get_live_url(url=None):
    if not url:
        url = os.environ.get('EVENT_URL')
    else:
        url = url
        print(url)
    ydl_opts = {}
    ydl_opts = {
        # 'outtmpl': '%(title)s.%(ext)s',
        'format': ' bestvideo[ext=mp4]+bestaudio[ext=mp4]/mp4',

    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                url, download=False)
            formats = meta.get('formats', [meta])

            for f in formats:
                # print(f)
                try:
                    if f['format_id'] == 'hls-fastly_live-2959':
                        # print(f'{f}\n\n')
                        return f
                    if 'hls' in f['format'] and f['ext'] == 'mp4' and f['vcodec'] != 'none' and f['acodec'] != 'none' and f['fps'] == 30 and f['width'] == 1920:
                        return f
                except KeyError:
                    pass
    except youtube_dl.utils.DownloadError:
        return None


def get_vimeo_roku_feed():
    url = os.environ.get('ROKU_FEED')
    response = requests.get(url)
    return response.json()


def get_injected_roku_feed():
    # live_blob = get_live_url()
    cur_roku_feed = get_vimeo_roku_feed()

    # if live_blob:
    est = timezone('US/Eastern')
    now = datetime.now(tz=Eastern)
    end_time = datetime.now(tz=Eastern) + timedelta(hours=2)
    # 2020-11-08T19:04:55-05:00 <- Expected Time format for Roku Direct Publisher
    now = datetime.strftime(now, '%Y-%m-%dT%H:%M:%S%z')
    end_time = datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%S%z')
    live_object = {"id": "cbctest1",
                   "title": "Live Stream",
                   "shortDescription": "Worship with us each Sunday at 10:00 AM EST.",
                   "thumbnail": "https://s3.amazonaws.com/hproku/images/live-stream-1280.png",
                   "genres": ["faith"], "tags": ["live"], "releaseDate": "2020-11-10",
                   "content": {"dateAdded": "2020-11-10T14:14:54.431Z",
                               "captions": [],
                               "duration": 230,
                               "videos": [{"url": "https://channelbuilder.church/live.m3u8",
                                           "quality": "HD",
                                           "videoType": "MP4"}]},
                   "validityPeriodStart": now,
                   "validityPeriodEnd": end_time}

    cur_roku_feed['liveFeeds'] = [live_object]

    return cur_roku_feed


if __name__ == "__main__":
    # print(get_live_url('https://vimeo.com/476960836'))
    print(get_live_url())

    # print(get_injected_roku_feed())
    # https: // vimeo.com / 477782549
    pass
