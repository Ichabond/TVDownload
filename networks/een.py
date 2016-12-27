import networks
import bs4
import json


class Een(networks.TVNetwork):

    def download_show(self, url):
        req = self.session.get(url)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        dl_id = soup.find("div", attrs={'data-video': True})
        req = self.session.get(self.url.format(**{'dl_id': dl_id['data-video']}))
        reply = json.loads(req.text)
        targets = reply['targetUrls']
        if 'subtitleUrls' in reply:
            r = self.session.get(reply['subtitleUrls'][0]['url'])
            if r.status_code == 200:
                with open('video_sub.vtt', 'wb') as f:
                    for chunk in r.iter_content(chunk_size=128):
                        f.write(chunk)

        for target in targets:
            if target['type'] == 'HLS':
                super().download_show_all(url=target['url'])

    def get_show_url(self, name):
        req = self.session.get(self.overview)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        for link in soup.find_all("a"):
            if link.h3 is not None:
                if name.lower() in link.h3.string.lower():
                    return link.get('href')


def init(config):
    return Een("een", config["een"]['download_url'], config["een"]['overview_url'])
