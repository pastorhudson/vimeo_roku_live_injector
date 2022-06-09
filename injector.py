from pprint import pprint

import vimeo
import os
import json
from dotenv import load_dotenv

load_dotenv('secrets.env')

v = vimeo.VimeoClient(
    token=os.environ.get('YOUR_ACCESS_TOKEN'),
    key=os.environ.get('YOUR_CLIENT_ID'),
    secret=os.environ.get('YOUR_CLIENT_SECRET',),
    per_page="500"
)


def get_events():
    # live_event_id = "387083"

    # Make the request to the server for the "/me" endpoint.
    # about_me = v.get(f'/me/live_events/{live_event_id}/m3u8_playback')

    response = v.get(f'/users/yourcbcfamily/videos')

    # Make sure we got back a successful response.
    assert response.status_code == 200

    # Load the body's JSON data.

    pretty_json = json.loads(response.text)
    # for object in pretty_json['data']:
    #     print(object['type'])
    for data in pretty_json['data']:
        if data['type'] == 'live' and data['transcode']['status'] == 'in_progress':
            print(f"{data['name']} - {data['link']} {data['modified_time']}")

            # print(json.dumps(data, indent=2))
    # print(about_me.json())


def get_videos():
    more = True
    # per_page = '?per_page=50'

    url = '/users/yourcbcfamily/videos?per_page=100'
    files = []

    while more:

        try:
            response = v.get(url)
        except Exception as e:
            print(f"request exception {e}")

        # Make sure we got back a successful response.
        assert response.status_code == 200

        # Load the body's JSON data.

        pretty_json = json.loads(response.text)

        try:
            pprint(pretty_json.get('paging').get('next'))
            # print(f"Videos: {len(pretty_json['data'])}")
            url = pretty_json.get('paging').get('next')

            if url:
                more = True
            else:
                more = False
        except Exception as e:
            print(e)
        for data in pretty_json['data']:
            if data['type'] == 'live' and data['transcode']['status'] == 'in_progress':
                print(f"{data['name']} - {data['link']} {data['modified_time']}")
            found_video = False
            for file in data['files']:
                if file['fps'] == 60 and file['public_name'] == '1080p':
                    files.append({"name": data['name'], "url": file['link']})
                    found_video = True
                if file['fps'] == 30 and file['public_name'] == '1080p' and not found_video:
                    files.append({"name": data['name'], "url": file['link']})
                    found_video = True
                elif file['fps'] == 30 and file['public_name'] == '720p' and not found_video:
                    files.append({"name": data['name'], "url": file['link']})
                    found_video = True

    return files


if __name__ == '__main__':
    videos = get_videos()
    print(len(videos))
    print(videos)
    # test()
