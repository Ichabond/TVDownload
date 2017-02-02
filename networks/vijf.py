import networks
import bs4


class Vijf(networks.ClosedTVNetwork):

    def login(self):
        form_req = self.session.get(self.login_url)
        soup = bs4.BeautifulSoup(form_req.text, "html.parser")
        form_build_id = soup.find("form", attrs={"id": "user-login"}).find("input",
                                                                           attrs={"name": "form_build_id"})['value']
        payload = {'name': self.username, 'pass': self.password, 'op': 'Inloggen',
                   'form_id': 'user_login', 'form_build_id': form_build_id}
        self.session.post(self.login_url, data=payload)
        self.logged_in = True
        return self.logged_in

    def download_show(self, url):
        if not self.logged_in:
            self.login()
        req = self.session.get(url)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        dl_id = soup.find("div", attrs={'data-filename': True})
        super().download_show_all(url_variables={'dl_id': dl_id['data-filename']})

    def get_show_url(self, name):
        req = self.session.get(self.overview)
        soup = bs4.BeautifulSoup(req.text, "html.parser")
        for link in soup.find_all("div", attrs={'class': "video-playlist-slideshow-block"}):
            if link.h1 is not None:
                if name.lower() in link.h1.string.lower():
                    link = link.find("div", attrs={'class': 'link-overlay'})
                    return "http://vijf.be"+link.a.get('href')


def init(config):
    return Vier("vijf", config["vijf"]["download_url"], config["vijf"]['overview_url'],
                config["vijf"]['login']['url'], config["vijf"]['login']['username'],
                config["vijf"]['login']['password'])