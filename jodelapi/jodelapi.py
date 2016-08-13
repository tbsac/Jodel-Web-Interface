
import json
import os
import requests

import jodelapi.location as location
import jodelapi.restapi as restapi

class Connection(object):

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = restapi.APP_CONFIG.user_agent
        self.user = None

    def set_proxy(self, proxy_ip):
        self.session.proxies = {"http": proxy_ip, "https": proxy_ip}

    def set_user(self, user):
        self.user = user

    def request(self, request_type, **kwargs):
        params = {**request_type.parameters, **kwargs}
        
        url = restapi.API_URL + request_type.version + "/" + request_type.url
        if request_type.postid:
            url += params["postid"] + "/"
        if request_type.country:
            url += params["country"] + "/"
        if request_type.postfix:
            url += request_type.postfix

        if params['payload']:
            data = json.dumps(params['payload'])
        else:
            data = None

        if request_type.noauth:
            self.session.headers['Authorization'] = None
            req = requests.Request(
                request_type.method, url, data=data)
        else:
            if not self.user:
                print("Attempted to send authenticated request without user!")
                return False
            self.session.headers['Authorization'] = self.user['token_type'] + " " + self.user['access_token']
            req = requests.Request(
                request_type.method, url,
                data=data,
                params=params['get_parameters'])

        try:
            prepared_req = self.session.prepare_request(req)
            prepared_req.headers = restapi.sign_request(prepared_req)
            prepared_req.headers["Content-Type"] = "application/json"

            response = self.session.send(prepared_req, timeout=10)

            if response.status_code == request_type.expect:
                if response.status_code == 204:
                    return True
                try:
                    return response.json()
                except ValueError as valueError:
                    print(str(valueError) + ': ' + url)
                    return None
            else:
                print("Request to " + url + " failed:")
                print("Status code: " + str(response.status_code))
                print("Text: " + response.text)
                return False
        except requests.exceptions.ConnectionError as connectionError:
            print("Sending request failed: " + str(connectionError))
            return False

    def create_user(self, device_uid, city, country): 
        payload = { 
            'client_id': restapi.CLIENT_ID,
            'device_uid': device_uid,
            'location': location.resolve_location(city, country),
        }
        return self.request(restapi.REGISTER, payload=payload)

    def upvote(self, postid):
        return self.request(restapi.UPVOTE, postid=postid)

    def popular_posts(self):
        return self.request(restapi.GET_POPULAR)

    def recent_posts(self):
        return self.request(restapi.GET_POSTS)
