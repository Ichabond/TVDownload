import networks
import re
import json
import urllib.parse


class Vtm(networks.ClosedTVNetwork):
    def __init__(self, api_endpoint, apikey, *args, **kwargs):
        self.endpoint = api_endpoint
        self.apikey = apikey
        self.access_token = None
        self.profile = None
        super(Vtm, self).__init__(*args, **kwargs)

    def login(self):
        payload = {"loginID": self.username, "password": self.password,
                   "ApiKey": self.apikey, "authMode": "cookie", "includeSSOToken": "true", "targetEnv": "jssdk",
                   "sessionExpiration": -2}
        resp = self.session.post(self.login_url, data=payload)
        json_data = resp.json()
        resp2 = self.session.get("http://static2.watch.stievie.be/config-1800581f9a7cf09aaa2219562fb8dd54.js")
        apikey = re.search('medialaan:{apiKey:\"(.+?)\"', resp2.text).group(1)
        headers = {"Authorization": "apikey=" + apikey}
        self.session.headers.update(headers)
        self.profile = json_data
        payload = {"database": "stievie-sso", "uid": json_data['UID'], "signature": json_data['UIDSignature'],
                   "timestamp": json_data['signatureTimestamp']}
        resp2 = self.session.get("http://user.medialaan.io/user/v1/gigya/request_token", params=payload)
        json_data2 = resp2.json()
        self.access_token = json_data2['response']
        self.logged_in = True
        return self.access_token

    def download_show(self, url):
        if not self.logged_in:
            self.login()
        req = self.session.get(url)
        video_json = re.search(b"var videoJSConfig = JSON.parse\('(.*)'\);", req.content).group(1)
        video_json = json.loads(video_json.decode('unicode_escape'))
        url = self.url.format(dl_id=video_json['vodId'], UID=self.profile['UID'],
                              UIDSig=urllib.parse.quote(self.profile['UIDSignature']),
                              timestamp=self.profile['signatureTimestamp'])
        url = self.session.get(url).json()['response']['uri']
        super().download_show_all(url=url)

    def get_show_url(self, name):
        raise NotImplementedError


def init(config):
    return Vtm(config["vtm"]["api_endpoint"], config["vtm"]['login']['apikey'], "vtm",
               config["vtm"]["download_url"], config["vtm"]['overview_url'],
               config["vtm"]['login']['url'], config["vtm"]['login']['username'],
               config["vtm"]['login']['password'])
