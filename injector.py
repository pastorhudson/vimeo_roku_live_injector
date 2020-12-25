import vimeo
import os
import json

v = vimeo.VimeoClient(
    token=os.environ.get('YOUR_ACCESS_TOKEN'),
    key=os.environ.get('YOUR_CLIENT_ID'),
    secret=os.environ.get('YOUR_CLIENT_SECRET')
)

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