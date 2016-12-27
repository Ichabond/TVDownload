import json


class Config(object):

    def __init__(self):
        self.config_dict = {}

    def load(self, filename):
        with open(filename) as data:
            self.config_dict = json.load(data)

    def add(self, key, value):
        self.config_dict[key] = value

    def keys(self):
        return self.config_dict.keys()

    def __getitem__(self, item):
        return self.config_dict[item]
