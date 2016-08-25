

import re
import hmac
import hashlib
import datetime



APP_VERSION = '4.14.1'
PORT = 443
CLIENT_ID = "81e8a76e-1e02-4d17-9ba0-8a7020261b26"
API_URL_BASE = 'api.go-tellm.com'
API_URL = 'https://' + API_URL_BASE + '/api/'

class ConfigEntry():
    def __init__(self, hmac_secret, version_string=None, user_agent_string=None, x_client_type=None, x_api_version='0.1'):
        if version_string is not None:
            if user_agent_string is None:
                user_agent_string = 'Jodel/'+version_string+' Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus 5 Build/MMB29V)'
            if x_client_type is None:
                x_client_type     = 'android_'+version_string

        if hmac_secret is None or len(hmac_secret) != 40:
            raise ValueError('The HMAC secret must be exactely 40 characters long')
        self.hmac_secret = hmac_secret
        self.user_agent = user_agent_string
        self.client_type = x_client_type
        self.api_version = x_api_version


# See https://bitbucket.org/cfib90/ojoc/
APP_CONFIG = ConfigEntry('jcUwaNNZwTSaMgbEEohXJhncvyIMdnZkFecWfPOU', version_string='4.14.1', x_api_version='0.2')


class APIMethod:

    def __init__(self, method, url, payload=None, expect=200, postid=None,country=None, postfix=None, noauth=None, get_parameters=None, version='v2'):
        self.method = method
        self.url = url
        self.payload = payload
        self.expect = expect
        self.postid = postid
        self.country = country
        self.postfix = postfix
        self.noauth = noauth
        self.get_parameters = get_parameters
        self.version = version
        self.parameters = {
            'payload': self.payload,
            'postid': self.postid,
            'country': self.country,
            'get_parameters': self.get_parameters
        }


SET_POSITION      = APIMethod('PUT', 'users/place/',     payload=True, expect=204)
UPVOTE            = APIMethod('PUT', 'posts/',           postid=True, postfix='upvote/')
PIN               = APIMethod('PUT', 'posts/',           postid=True, postfix='pin/')
DOWNVOTE          = APIMethod('PUT', 'posts/',           postid=True, postfix='downvote/')
UNPIN             = APIMethod('PUT', 'posts/',           postid=True, postfix='unpin/')
REGISTER          = APIMethod('POST', 'users/',          payload=True, noauth=True)
NEW_POST          = APIMethod('POST', 'posts/',          payload=True)
DELETE_POST       = APIMethod('DELETE', 'posts/',        postid=True, expect=204)
GET_KARMA         = APIMethod('GET', 'users/karma/')
GET_POSTS         = APIMethod('GET', 'posts/')
GET_COMBO         = APIMethod('GET', 'posts/location/combo/')
GET_POPULAR       = APIMethod('GET', 'posts/location/popular/')
GET_DISCUSSED     = APIMethod('GET', 'posts/location/discussed/')
GET_COUNTRY_POSTS = APIMethod('GET', 'feed/country/',    country=True)
GET_POST          = APIMethod('GET', 'posts/',           postid=True)
GET_MY_POSTS      = APIMethod('GET', 'posts/mine/')
GET_MY_REPLIES    = APIMethod('GET', 'posts/mine/replies/')
GET_MY_VOTES      = APIMethod('GET', 'posts/mine/votes/')
GET_MY_POPULAR    = APIMethod('GET', 'posts/mine/popular/')
GET_MY_DISCUSSED  = APIMethod('GET', 'posts/mine/discussed/')
GET_CHANNEL       = APIMethod('GET', 'posts/channel/combo', get_parameters=True, version='v3')
GET_PINNED        = APIMethod('GET', 'posts/mine/pinned/')
GET_USER_CONFIG   = APIMethod('GET', 'user/config',      version='v3')


def sign_request(prep_req):
    """ Performs HMAC signing of a prepared request object. """

    # Requesting the first access token must now be done with a HMAC signed request
    #
    # Signing works as follows:
    #
    # 1. Retrieve a _secret_ for HMAC
    #    This is done by using an opaque C++ library in the original
    #    Android app. The app's signature hash is fed into the
    #    library and a secret falls out.
    #
    # 2. Stringify the request. this is done using the following scheme:
    #
    #    <METHOD>%<URL-BASE>%<PORT>%<PATH-with-trailing-slash>%<BEARER-token-if-exists>%<T-Z-UTC-timestamp>%<LIST-of-GET-keys-and-vals-separated-by-percent>%<REQUEST-DATA>
    #
    # 3. Calculate the HMAC-SHA1 digest of the stringified request
    #
    # 4. Add the headers 'X-Client-Type', 'X-Api-Version' and 'X-Authorization'
    #    'X-Authorization' has the value 'HMAC <uppercase hex representation of HMAC digest>'
    #
    # 5. Send the request with the headers

    # Collect the parameters over which to calculate the HMAC
    headers = prep_req.headers
    body = prep_req.body
    url = prep_req.url
    method = prep_req.method

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    authheader = headers.get('Authorization')
    if authheader is not None:
        auth = (authheader.split(" "))[1]
    else:
        auth = ""

    parameter_start = url.find('?')
    if parameter_start == -1:
        parameters = ""
        path_end = len(url)
    else:
        parameters = re.sub('[&=]', '%', url[parameter_start + 1:])
        path_end = parameter_start

    # do black signing magic -- HMAC
    # 7 -> "https://"

    path_start = url.find('/', 8)

    if path_start == -1 or path_start == path_end:
        path = ""
    else:
        path = url[path_start:path_end]

    if body is None:
        body = ""

    # Construct the base for the HMAC hash: A percent-sign separated string containing the
    # paramters
    message = method.upper() + "%" + API_URL_BASE + "%" + str(PORT) + \
        "%" + path + "%" + auth + "%" + timestamp + "%" + parameters + "%" + body
    message = bytes(message, 'utf-8')
    dig = hmac.new(bytes(APP_CONFIG.hmac_secret, 'utf-8'),msg=message,digestmod=hashlib.sha1)

    # Append the headers
    headers['X-Client-Type'] = APP_CONFIG.client_type
    headers['X-Api-Version'] = APP_CONFIG.api_version
    headers['X-Timestamp'] = timestamp
    headers['X-Authorization'] = 'HMAC ' + str(dig.hexdigest()).upper()

    return headers
