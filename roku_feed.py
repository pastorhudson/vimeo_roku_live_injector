from flask import Flask, redirect, render_template
from get_url import get_injected_roku_feed, get_vimeo_live_url, get_offline_content
from cloudflare import get_live_stream
import dotenv
import os
from flask_cors import CORS
dotenv.load_dotenv(dotenv_path='secrets.env')
app = Flask(__name__)

CORS(app)

@app.route('/rokufeed')
def roku_feed():
    return get_injected_roku_feed()


@app.route('/firetvfeed')
def amazonfire_feed():
    return get_injected_roku_feed()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/live.m3u8')
def hls_live():
    live_feed_url = get_live_stream('hls')
    if live_feed_url:
        return redirect(live_feed_url, code=302)
    else:
        offline_url = get_live_stream('hls')
        return redirect(offline_url, code=302)


@app.route('/live.mpd')
def dash_live():
    live_feed_url = get_live_stream('dash')
    if live_feed_url:
        return redirect(live_feed_url, code=302)
    else:
        offline_url = get_live_stream('dash')
        return redirect(offline_url, code=302)


if __name__ == '__main__':
    app.run()

