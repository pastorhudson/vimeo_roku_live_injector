from injector import get_videos
from cloudflare import upload_by_link

videos = get_videos()

for video in videos:
    print(f"Uploading {video['name']}")
    upload_by_link(video['url'], video['name'])
