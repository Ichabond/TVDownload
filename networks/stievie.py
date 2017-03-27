import networks
import re
from urllib.parse import urljoin

class Stievie(networks.ClosedTVNetwork):

    def __init__(self, api_endpoint, apikey, *args, **kwargs):
        self.endpoint = api_endpoint
        self.apikey = apikey
        self.access_token = None
        super(Stievie, self).__init__(*args, **kwargs)

    def login(self):
        payload = {"loginID": self.username, "password": self.password,
                   "ApiKey": self.apikey, "authMode": "cookie", "includeSSOToken": "true", "targetEnv": "jssdk",
                   "sessionExpiration": -2}
        resp = self.session.post(self.login_url, data=payload)
        json_data = resp.json()
        resp2 = self.session.get("https://static1.watch.stievie.be/config-e8d98d8d241a3ea85670672d469ef3f4.js")
        apikey = re.search('medialaan:{apiKey:\"(.+?)\"', resp2.text).group(1)
        headers = {"Authorization": "apikey="+apikey}
        self.session.headers.update(headers)
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
        super().download_show_all(url=url)

    def get_show_url(self, name):
        if not self.logged_in:
            self.login()
        program_id = 0
        season_number = [0, ""]
        episode_id = 0
        progs = self.session.get("http://vod.medialaan.io/vod/v2/programs?channels[]=vtm&channels[]=2be"
                                 "&channels[]=vitaya&limit=0")
        for video in progs.json()['response']['videos']:
            if name in video['title']:
                program_id = video['id']
        progs = self.session.get(urljoin(self.endpoint, "programs/{progID}/seasons".format(progID=program_id)))
        for season in progs.json()['response']['seasons']:
            if season_number[0] <= int(season['number']):
                season_number[0] = int(season['number'])
                season_number[1] = season['id']
        # 257059160182000
        progs = self.session.get(urljoin(self.endpoint, "videos?limit=0&sort=broadcastDate&sortDirection=asc"
                                 "&episodeIds{progID}&seasonIds={seasonID}".format(progID=program_id,
                                                                                   seasonID=season_number[1])))
        for episode in progs.json()['response']['videos']:
            if episode_id < int(episode['episode']['id']):
                episode_id = int(episode['episode']['id'])
        progs = self.session.get(urljoin(self.endpoint, "videos?episodeIds={episodeID}".format(episodeID=episode_id)))
        for video in progs.json()['response']['videos']:
            if episode_id < int(episode['id']):
                episode_id = int(episode['id'])    
        self.session.headers['Authorization'] += "&access_token=" + self.access_token
        progs = self.session.get(urljoin(self.endpoint, "videos/{progID}/watch".format(progID=episode_id)))
        return progs.json()['response']['hls-encrypted']['url']


def init(config):
    return Stievie(config["stievie"]["api_endpoint"], config["stievie"]['login']['apikey'], "stievie",
                   config["stievie"]["download_url"], config["stievie"]['overview_url'],
                   config["stievie"]['login']['url'], config["stievie"]['login']['username'],
                   config["stievie"]['login']['password'])
