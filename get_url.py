import youtube_dl
import os
import requests


def get_live_url():
    url = os.environ.get('EVENT_URL')
    ydl_opts = {}
    ydl_opts = {
        # 'outtmpl': '%(title)s.%(ext)s',
        'format': ' bestvideo[ext=mp4]+bestaudio[ext=mp4]/mp4',

    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(
            url, download=False)
        formats = meta.get('formats', [meta])
    for f in formats:
        # print(f)
        try:
            # if 'hls' in f['format'] and f['ext'] == 'mp4' and f['vcodec'] != 'none' and f['acodec'] != 'none' and f['fps'] == 30 and f['width'] == 1920:
            if f['format_id'] == 'hls-fastly_live-2959':
                # print(f'{f}\n\n')
                return f['manifest_url']
        except KeyError:
            pass


def get_vimeo_roku_feed():
    url = os.environ.get('ROKU_FEED')
    response = requests.get(url)
    return response.json()


def get_injected_roku_feed():
    live_url = get_live_url()
    live_object = {"id": "20201108",
                   "title": "Live Stream",
                   "shortDescription": "Worship with us each Sunday at 10:00 AM EST.",
                   "thumbnail": "https://s3.amazonaws.com/hproku/images/live-stream-1280.png",
                   "genres": ["faith"], "tags": ["live"], "releaseDate": "2016-06-01",
                   "content": {"dateAdded": "2020-02-07T14:14:54.431Z",
                               "captions": [],
                               "duration": 230,
                               "videos": [{"url": live_url,
                                           "quality": "HD",
                                           "videoType": "HLS"}]}}

    cur_roku_feed = get_vimeo_roku_feed()
    cur_roku_feed['movies'].append(live_object)

    return cur_roku_feed


if __name__ == "__main__":
    print(get_live_url())
    # print(get_injected_roku_feed(477782549))
    # https: // vimeo.com / 477782549
    pass

