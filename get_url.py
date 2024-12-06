import youtube_dl
import os
import requests
from datetime import datetime, timedelta
from pytz import timezone
# from pytz.reference import Eastern
from cloudflare import generate_cloudflare_roku_feed
from pytz.reference import Eastern
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom


def get_cloudflare_url(url=None):
    if not url:
        url = os.environ.get('EVENT_URL')
    else:
        url = url
        print(url)


def get_vimeo_live_url(url=None):
    if not url:
        url = os.environ.get('EVENT_URL')
    else:
        url = url
        print(url)
    # ydl_opts = {}
    ydl_opts = {
        # 'outtmpl': '%(title)s.%(ext)s',
        # 'format': ' bestvideo[ext=mp4]+bestaudio[ext=mp4]/mp4',

    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                url, download=False)
            formats = meta.get('formats', [meta])
            tbr = 1
            best = None
            try:
                for f in formats:
                    if 'audio' not in f['format_id'] and f['tbr'] and 'dash' not in f['format_id']:
                        if int(f['tbr']) > tbr:
                            best = f
                            tbr = int(f['tbr'])
            except KeyError:
                return None

            return best

    except youtube_dl.utils.DownloadError:
        return None


def get_vimeo_roku_feed():
    url = os.environ.get('ROKU_FEED')
    response = requests.get(url)
    return response.json()


def get_injected_roku_feed():
    # live_blob = get_live_url()
    cur_roku_feed = generate_cloudflare_roku_feed()

    # if live_blob:
    est = timezone('US/Eastern')
    now = datetime.now(tz=Eastern)
    end_time = datetime.now(tz=Eastern) + timedelta(hours=24)
    # 2020-11-08T19:04:55-05:00 <- Expected Time format for Roku Direct Publisher
    release_now = datetime.strftime(now, '%Y-%m-%d')
    now = datetime.strftime(now, '%Y-%m-%dT%H:%M:%S%z')
    end_time = datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%S%z')

    live_object = {"id": "cbctest3",
                   "title": "Live Stream",
                   "shortDescription": "Worship with us each Sunday at 10:00 AM EST.",
                   "thumbnail": "https://images.squarespace-cdn.com/content/v1/5000d51de4b0392912a47ef2/1605108881444-GSZYHESIKEAT6TLX8TS2/ke17ZwdGBToddI8pDm48kNvT88LknE-K9M4pGNO0Iqd7gQa3H78H3Y0txjaiv_0fDoOvxcdMmMKkDsyUqMSsMWxHk725yiiHCCLfrh8O1z5QPOohDIaIeljMHgDF5CVlOqpeNLcJ80NK65_fV7S1UbeDbaZv1s3QfpIA4TYnL5Qao8BosUKjCVjCf8TKewJIH3bqxw7fF48mhrq5Ulr0Hg/cbclive.png",
                   "genres": ["faith"], "tags": ["live"],
                   "releaseDate": release_now,
                   "content": {"dateAdded": now,
                               "captions": [],
                               "duration": 5000,
                               "videos": [
                                   # {"url": "https://roku.cbcfamily.church/live.m3u8",
                                   #  "quality": "HD",
                                   #  "videoType": "HLS"},
                                   {"url": "https://roku.cbcfamily.church/live.mpd",
                                    "quality": "FHD",
                                    "videoType": "DASH"}
                               ]
                               },

                   "validityPeriodStart": now,
                   "validityPeriodEnd": end_time}

    cur_roku_feed['liveFeeds'] = [live_object]
    cur_roku_feed['lastUpdated'] = now

    return cur_roku_feed


def get_offline_content():
    est = timezone('US/Eastern')
    now = datetime.now(tz=Eastern)
    end_time = datetime.now(tz=Eastern) + timedelta(hours=24)
    # 2020-11-08T19:04:55-05:00 <- Expected Time format for Roku Direct Publisher
    now = datetime.strftime(now, '%Y-%m-%dT%H:%M:%S%z')
    end_time = datetime.strftime(end_time, '%Y-%m-%dT%H:%M:%S%z')
    offline_content = {
        "id": "478125860",
        "title": "Live Stream Offline",
        "shortDescription": "Find hope every Sunday at 10am with Calvary Baptist Church.",
        "thumbnail": "https://i.vimeocdn.com/video/992886664_800x450.png",
        "releaseDate": now,
        "genres": [
            "faith"
        ],
        "tags": [
            "faith"
        ],
        "content": {
            "dateAdded": now,
            "duration": 24,
            "videos": [
                {
                    "url": "https://player.vimeo.com/external/478125860.hd.mp4?s=017c1c0870b85022036b83fdadaa7a2e36a6875c&profile_id=175",
                    "quality": "FHD",
                    "videoType": "MP4",
                    "bitrate": 4860265
                }
            ]
        }
    }
    return "https://143vod-adaptive.akamaized.net/exp=1605126373~acl=%2Fea26be3b-4680-4ce4-b24b-d5df9cb78c7e%2F%2A~hmac=a1f84823cadb5590d868cf88ec4250e2bb8b88a841b2dff47c8a606c187e569d/ea26be3b-4680-4ce4-b24b-d5df9cb78c7e/video/f2940ff3/playlist.m3u8"


def get_categories():
    # Create the root element
    root = Element('categories')

    # Add XML declaration processing instruction

    # Add banner_ad element with comment
    banner_comment = Comment(' banner_ad: optional element which displays an at the top level category screen ')
    root.append(banner_comment)

    banner = SubElement(root, 'banner_ad')
    banner.set('sd_img', 'https://devtools.web.roku.com/videoplayer/images/missing.png')
    banner.set('hd_img', 'https://devtools.web.roku.com/videoplayer/images/missing.png')

    # Technology category
    tech = SubElement(root, 'category')
    tech.set('title', 'Live')
    tech.set('description', 'Live Service')
    tech.set('sd_img', 'https://devtools.web.roku.com/videoplayer/images/TED_Technology.png')
    tech.set('hd_img', 'https://devtools.web.roku.com/videoplayer/images/TED_Technology.png')

    tech_mind = SubElement(tech, 'categoryLeaf')
    tech_mind.set('title', 'Services')
    tech_mind.set('description', '')
    tech_mind.set('feed', 'https://roku.cbcfamily.church/feed.xml')

    # tech_global = SubElement(tech, 'categoryLeaf')
    # tech_global.set('title', 'Global Issues')
    # tech_global.set('description', '')
    # tech_global.set('feed', 'https://devtools.web.roku.com/videoplayer/xml/globalissues.xml')
    #
    # # Entertainment category
    # ent = SubElement(root, 'category')
    # ent.set('title', 'Entertainment')
    # ent.set('description', 'TED Talks on Entertainment')
    # ent.set('sd_img', 'https://devtools.web.roku.com/videoplayer/images/TED_Entertainment.png')
    # ent.set('hd_img', 'https://devtools.web.roku.com/videoplayer/images/TED_Entertainment.png')
    #
    # ent_music = SubElement(ent, 'categoryLeaf')
    # ent_music.set('title', 'Music')
    # ent_music.set('description', '')
    # ent_music.set('feed', 'https://devtools.web.roku.com/videoplayer/xml/music.xml')
    #
    # ent_insp = SubElement(ent, 'categoryLeaf')
    # ent_insp.set('title', 'Inspiration')
    # ent_insp.set('description', '')
    # ent_insp.set('feed', 'https://devtools.web.roku.com/videoplayer/xml/inspiration.xml')
    #
    # # Design category
    # design = SubElement(root, 'category')
    # design.set('title', 'Design')
    # design.set('description', 'TED Talks on Design')
    # design.set('sd_img', 'https://devtools.web.roku.com/videoplayer/images/TED_Design.png')
    # design.set('hd_img', 'https://devtools.web.roku.com/videoplayer/images/TED_Design.png')
    #
    # design_create = SubElement(design, 'categoryLeaf')
    # design_create.set('title', 'Creativity')
    # design_create.set('description', '')
    # design_create.set('feed', 'https://devtools.web.roku.com/videoplayer/xml/creativity.xml')
    #
    # design_leaf = SubElement(design, 'categoryLeaf')
    # design_leaf.set('title', 'Design')
    # design_leaf.set('description', '')
    # design_leaf.set('feed', 'https://devtools.web.roku.com/videoplayer/xml/design.xml')

    # Convert to string with pretty printing
    xml_str = minidom.parseString(tostring(root, encoding='unicode')).toprettyxml(indent='  ')

    # Add XML declaration since toprettyxml() doesn't include it
    if not xml_str.startswith('<?xml'):
        xml_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml_str

    return xml_str


if __name__ == "__main__":
    # print(get_vimeo_roku_feed())
    # print(get_live_url('https://vimeo.com/494519730'))
    # offline_url = get_live_url(os.environ.get('OFFLINE_URL'))
    # print(offline_url)
    # print(get_live_url('https://vimeo.com/478184394'))
    print(get_categories())

    # print(get_injected_roku_feed())
    # https: // vimeo.com / 477782549
    pass
