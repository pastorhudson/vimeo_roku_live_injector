from flask import Flask, redirect
from get_url import get_injected_roku_feed, get_live_url, get_offline_content
import dotenv
import os
dotenv.load_dotenv(dotenv_path='secrets.env')
app = Flask(__name__)


@app.route('/')
def channel_feed():
    return get_injected_roku_feed()


@app.route('/live.m3u8')
def live():
    # return redirect(get_offline_content(), 302)
    live_feed_url = get_live_url()
    if live_feed_url:
        return redirect(live_feed_url['manifest_url'], code=302)
    else:
        offline_url = get_live_url(os.environ.get('OFFLINE_URL'))
        return redirect(offline_url['url'], code=301)


if __name__ == '__main__':
    app.run()
