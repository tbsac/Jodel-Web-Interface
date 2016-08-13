
import re
import os
import sys
import json
from os.path import join, realpath, dirname, isfile

import jodelapi.bot_helper as bot_helper
import jodelapi.jodelapi as api


API_METHODS = {}
GLOBAL_CONN = None
USER_AUTH = {}
USER_DEVICE_UID = None

def apipath(pth):
    regexp = re.compile("^" + pth.replace("?", "([a-zA-Z0-9]+)") + "$")
    def _inner(method):
        API_METHODS[regexp] = method
        return method
    return _inner


def init_conn():
    global GLOBAL_CONN, USER_AUTH, USER_DEVICE_UID
    GLOBAL_CONN = api.Connection()
    token_file = join(realpath(dirname(__file__)), "web_user.token")
    if isfile(token_file):
        with open(token_file) as handle:
            print(bot_helper.colored_text("Loading from token file", "Magenta"))
            data = json.load(handle)
            USER_DEVICE_UID = data["device_uid"]
            USER_AUTH = data["auth"]
    else:
        print(bot_helper.colored_text("Creating new user", "Yellow"))
        USER_DEVICE_UID = bot_helper.make_random_device_uid()
        USER_AUTH = GLOBAL_CONN.create_user(USER_DEVICE_UID, "Aachen", "DE")
        if not USER_AUTH:
            print(bot_helper.colored_text("Failed to create user for webserver!", "Red"))
            sys.exit(-1)
        else:
            payload = {"device_uid": USER_DEVICE_UID, "auth": USER_AUTH}
            with open(token_file, "w") as handle:
                json.dump(payload, handle, indent=2)

    print("Device UID is", bot_helper.colored_text(USER_DEVICE_UID, "Yellow"))
    print("Access token is", bot_helper.colored_text(USER_AUTH["access_token"], "Green"))
    print("Distinct id is", bot_helper.colored_text(USER_AUTH["distinct_id"], "Magenta"))

    GLOBAL_CONN.set_user(USER_AUTH)

init_conn()


@apipath("/posts/popular/")
def get_popular_posts():
    return GLOBAL_CONN.popular_posts()

@apipath("/posts/recent/")
def get_recent_posts():
    return GLOBAL_CONN.recent_posts()

@apipath("/post/?/")
def get_particular_post(post_id):
    return { "post_id": post_id }
