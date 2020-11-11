from flask import Flask
from get_url import get_injected_roku_feed
import dotenv
import os
dotenv.load_dotenv(dotenv_path='secrets.env')
app = Flask(__name__)


@app.route('/')
def channel_feed():
    return get_injected_roku_feed()


if __name__ == '__main__':
    app.run()