
import os
from os.path import isdir, join, dirname, realpath
import json
import time
import random


from .colorama import init, Fore, Back, Style
init()

random.seed(time.time())

BASEDIR = join(dirname(realpath(__file__)), "..")

TOKEN_FILE_SUFFIX = ".token"
DATA_FOLDER = join(BASEDIR, "data")
TOKEN_FOLDER = join(BASEDIR, "data", "tokens")

def save_auth(device_uid, auth):
    if not isdir(TOKEN_FOLDER):
        os.makedirs(TOKEN_FOLDER)
    with open(join(TOKEN_FOLDER, device_uid + TOKEN_FILE_SUFFIX), "w") as handle:
        json.dump(auth, handle, indent=2)

def load_auth(device_uid):
    with open(join(TOKEN_FOLDER, device_uid + TOKEN_FILE_SUFFIX)) as handle:
        return json.load(handle)

def get_all_device_uids():
    files = os.listdir(TOKEN_FOLDER)
    uids = []
    for f in files:
        if f.endswith(TOKEN_FILE_SUFFIX):
            uids.append(f.replace(TOKEN_FILE_SUFFIX, ""))
    return uids

def make_random_device_uid():
    id_bytes = os.urandom(32)
    id_bytes_str = ["%02x" % byte for byte in id_bytes]
    return ''.join(id_bytes_str)

def get_random_proxy():
    with open(join(DATA_FOLDER, "proxies.txt")) as handle:
        proxies = handle.read().replace("\r", "").strip().split("\n")
        return random.choice(proxies)

def colored_text(text, color="Red"):
    return getattr(Fore, color.upper()) + Style.BRIGHT + text + Style.RESET_ALL
