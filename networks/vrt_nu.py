import networks


class VrtNu(networks.ClosedTVNetwork):

    def __init__(self, apikey, *args, **kwargs):
        self.apikey = apikey
        super(VrtNu, self).__init__(*args, **kwargs)

    def login(self):
        payload = {"loginID": self.username, "password": self.password,
                   "ApiKey": self.apikey, "authMode": "cookie", "includeSSOToken": "true", "targetEnv": "jssdk",
                   "sessionExpiration": -2}
        resp = self.session.post(self.login_url, data=payload)
        json_data = resp.json()
        token = json_data['sessionInfo']['login_token']
        pl2 = {"uid": json_data["UID"], "uidsig": json_data["UIDSignature"], "ts": json_data["signatureTimestamp"],
               "fn": json_data["profile"]['firstName'], "ln": json_data["profile"]['lastName'],
               "email": json_data["profile"]['email']}
        cookie = {"glt_" + self.apikey: token}
        headers = {"Origin": 'https://www.vrt.be',
                   "Referer": "https://www.vrt.be/vrtnu/"}
        resp2 = self.session.post("https://token.vrt.be", cookies=cookie, json=pl2, headers=headers)
        if resp2.status_code == 200:
            self.logged_in = True
        else:
            self.logged_in = False
        return self.logged_in

    def download_show(self, url):
        if not self.logged_in:
            self.login()
        req = self.session.get(url[:-1]+".securevideo.json")
        json_resp = req.json()
        data = next(iter(json_resp.values()))
        req = self.session.get(self.url.format(**{'dl_id': data['mzid']}))
        reply = req.json()
        targets = reply['targetUrls']
        if reply['subtitleUrls']:
            r = self.session.get(reply['subtitleUrls'][0]['url'])
            if r.status_code == 200:
                with open('video_sub.vtt', 'wb') as f:
                    for chunk in r.iter_content(chunk_size=128):
                        f.write(chunk)
            for target in targets:
                if target['type'] == 'HLS':
                    super().download_show_all(url=target['url'])

    def get_show_url(self, name):
        raise NotImplementedError


def init(config):
    return VrtNu(config["vrt"]['login']['apikey'], "vrt", config["vrt"]["download_url"], config["vrt"]['overview_url'],
                 config["vrt"]['login']['url'], config["vrt"]['login']['username'],
                 config["vrt"]['login']['password'])
