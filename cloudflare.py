import json
import os

import requests
from pprint import pprint
from dotenv import load_dotenv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

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


def get_live_streams():
    pass


def get_all_videos():
    token = os.getenv('CLOUDFLARE_TOKEN')
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json',
    }

    response = requests.get(f'https://api.cloudflare.com/client/v4/accounts/{os.getenv("CLOUDFLARE_ACCOUNT")}/stream?after=2014-01-02T02:20:00Z&before=2023-01-02T02:20:00Z&include_counts=true', headers=headers)

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
                    "thumbnail": video['thumbnail'],
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
                        "duration": video['duration'],
                        "videos": [
                            {
                                "url": video['playback']['hls'],
                                "quality": "FHD",
                                "videoType": "HLS",
                                "bitrate": None
                            }
                        ]
                    }
                },
    return roku_data


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


if __name__ == "__main__":
    url = 'https://player.vimeo.com/progressive_redirect/download/714961469/container/1a96868c-8e53-4db8-ace0-a5e10c13ba2c/194cc380/every_day_-_week_5.mp4%20%281080p%29.mp4?expires=1654789709&loc=external&signature=edc0ac34553d41afa2c365e28d652df4c625cdf9f7f617ffb36f63e6ced1ea34'
    # pprint(get_all_videos())
    # good_token = verify_token(os.getenv('CLOUDFLARE_TOKEN'))
    # print(good_token)

    pprint(generate_cloudflare_roku_feed())
