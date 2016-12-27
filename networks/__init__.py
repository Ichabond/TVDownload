import abc
import py_hls_fetch.hls_fetch
import os
import requests


class TVNetwork(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, url, overview):
        self.name = name
        self.url = url
        self.overview = overview
        self.session = requests.Session()

    def download_show_all(self, url=None, url_variables=None):
        cwd = os.getcwd()
        if url:
            py_hls_fetch.hls_fetch.hls_fetch(url, cwd)
        else:
            py_hls_fetch.hls_fetch.hls_fetch(self.url.format(**url_variables), cwd)

    @abc.abstractmethod
    def download_show(self, url):
        """Implement the actual downloading of a show"""

    @abc.abstractmethod
    def get_show_url(self, name):
        """Retrieve show url from overview page"""


class ClosedTVNetwork(TVNetwork):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, url, overview, login_url, username, password):
        self.username = username
        self.password = password
        self.login_url = login_url
        self.logged_in = False
        super().__init__(name, url, overview)

    @abc.abstractmethod
    def login(self):
        """Should login to site"""

    @abc.abstractmethod
    def download_show(self, url):
        """Implement the actual downloading of a show"""
