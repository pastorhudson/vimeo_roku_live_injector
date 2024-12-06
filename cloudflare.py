import json
import os

import requests
from pprint import pprint
from dotenv import load_dotenv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
from xml.dom import minidom


load_dotenv('secrets.env')


def verify_token(token: str):
    """
    Takes a token and verifies that it is good.
    :param token:
    :return: True if token is good, False if it's bad.
    """

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    response = requests.get('https://api.cloudflare.com/client/v4/user/tokens/verify', headers=headers)

    return response.json()['success']


def upload_by_link(url: str, title: str):
    token = os.getenv('CLOUDFLARE_TOKEN')
    account = os.getenv('CLOUDFLARE_ACCOUNT')
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {"url": url,
            "meta": {"name": title}
            }

    response = requests.post(f'https://api.cloudflare.com/client/v4/accounts/{account}/stream/copy', headers=headers,
                             data=json.dumps(data))

    pprint(response.json())


def get_live_stream(type):
    videos = get_all_videos()
    for video in videos['result']['videos']:
        if video['status']['state'] == 'live-inprogress':
            return video['playback'][type]
        """https://videodelivery.net/76d46e1adafe66552d3eb93a4de1376b/manifest/video.m3u8"""
    if type == 'dash':
        return 'https://cloudflarestream.com/5a18891c41abda848b3f14197c15374b/manifest/video.mpd'
    if type == 'hls':
        return 'https://cloudflarestream.com/5a18891c41abda848b3f14197c15374b/manifest/video.m3u8'


def get_all_videos():

    token = os.getenv('CLOUDFLARE_TOKEN')
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
    }

    response = requests.get(f'https://api.cloudflare.com/client/v4/accounts/{os.getenv("CLOUDFLARE_ACCOUNT")}/stream?include_counts=true', headers=headers)

    return response.json()


def delete_all_videos():
    token = os.getenv("CLOUDFLARE_TOKEN")
    account = os.getenv("CLOUDFLARE_ACCOUNT")
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
    }
    videos = get_all_videos()['result']['videos']

    for video in videos:
        print(f"DELETE {video['uid']}")

        response = requests.delete(
            f'https://api.cloudflare.com/client/v4/accounts/{account}/stream/{video["uid"]}',
            headers=headers)


def parse_video(video):
    eastern = ZoneInfo("America/New_York")
    stamp = datetime.fromisoformat(video['created'].split(".")[0]).replace(tzinfo=timezone.utc).astimezone(eastern)
    stamp = datetime.strftime(stamp, "%Y-%m-%dT%H:%M:%S%z")
    roku_data = {
                    "id": video['uid'],
                    "title": video['meta']['name'],
                    "shortDescription": video['meta']['name'],
                    "thumbnail": video['thumbnail'] + "?height=450",
                    # "releaseDate": "2020-11-01T11:11:25-05:00",
                    "releaseDate": stamp,

                    "genres": [
                        "faith"
                    ],
                    "tags": [
                        "faith"
                    ],
                    "content": {
                        "dateAdded": stamp,
                        "duration": int(video['duration']),
                        "videos": [
                            {
                                "url": video['playback']['dash'],
                                "quality": "FHD",
                                "videoType": "DASH",
                                "bitrate": None
                            }
                        ],
                        "language": "en-US",
                    }
                },
    return roku_data[0]


def generate_cloudflare_roku_feed():
    videos = get_all_videos()
    feed = {
        "providerName": "Calvary Baptist Church",
        "lastUpdated": "2022-05-22T13:37:54-04:00",
        "language": "en",
        "movies": [
        ]
    }

    for video in videos['result']['videos']:
        print(video)
        feed['movies'].append(parse_video(video))

    return feed


def create_xml_structure(json_data):
    # Create root element
    root = ET.Element("feed")

    # Add result length and end index
    ET.SubElement(root, "resultLength").text = str(json_data['result']['total'])
    ET.SubElement(root, "endIndex").text = str(json_data['result']['range'])

    # Process each video
    for video in json_data['result']['videos']:
        item = create_video_item(video)
        root.append(item)

    return root


def create_video_item(video):
    # Create item element
    item = ET.Element("item")

    # Get thumbnail URL
    thumbnail_url = video['thumbnail']
    item.set("sdImg", thumbnail_url)
    item.set("hdImg", thumbnail_url)

    # Extract title from filename, removing extension
    title = video['meta'].get('name', '').replace('.mp4', '')
    ET.SubElement(item, "title").text = title

    # Create unique content ID from video UID (first 5 characters)
    ET.SubElement(item, "contentId").text = video['uid'][:5]

    # Add standard content information
    ET.SubElement(item, "contentType").text = "Video"
    ET.SubElement(item, "contentQuality").text = "HD"
    ET.SubElement(item, "streamFormat").text = "mp4"

    # Add media information
    media = ET.SubElement(item, "media")
    ET.SubElement(media, "streamQuality").text = "HD"
    ET.SubElement(media, "streamBitrate").text = "5000"
    ET.SubElement(media, "streamUrl").text = video['playback']['hls']

    # Add synopsis (using filename as description)
    ET.SubElement(item, "synopsis").text = title

    # Add genres (using a default value)
    ET.SubElement(item, "genres").text = "Church Service"

    # Add runtime (duration in seconds, rounded to nearest integer)
    ET.SubElement(item, "runtime").text = str(int(round(video['duration'])))

    return item


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


def get_xml_feed():
    # Here you would normally fetch your JSON data from your source
    # For this example, we'll assume json_data is available
    json_data = get_all_videos()
    # Create XML structure
    root = create_xml_structure(json_data)

    # Convert to pretty XML
    xml_str = prettify_xml(root)

    return xml_str

if __name__ == "__main__":
    # url = 'https://player.vimeo.com/progressive_redirect/download/714961469/container/1a96868c-8e53-4db8-ace0-a5e10c13ba2c/194cc380/every_day_-_week_5.mp4%20%281080p%29.mp4?expires=1654789709&loc=external&signature=edc0ac34553d41afa2c365e28d652df4c625cdf9f7f617ffb36f63e6ced1ea34'
    # pprint(get_live_stream('dash'))
    # good_token = verify_token(os.getenv('CLOUDFLARE_TOKEN'))
    # print(good_token)
    # pprint(get_all_videos())
    # pprint(generate_cloudflare_roku_feed())
    # clean_names()
    pprint(generate_cloudflare_roku_feed())
    # pprint(get_xml_feed())
