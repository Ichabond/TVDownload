import argparse
import os
import sys
from configuration import Config
import urllib.parse


def find_networks():
    modules = [m for m in os.listdir(os.path.join(sys.path[0], "networks/")) if m.endswith(".py")]
    return modules


def load_networks(config):
    env = {}
    ns = {}
    for network in find_networks():
        with open(os.path.join(os.path.join(sys.path[0], "networks/"), network)) as py_file:
            code = compile(py_file.read(), network, 'exec')
            exec(code, env, env)
            ns[network.split(".")[0]] = [env]
            if "init" in env:
                ns[network.split(".")[0]][0] = env['init'](config)
    return ns


def load_configuration():
    configuration = Config()
    configuration.load('main_config.json')
    return configuration


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--network", help="Network to download from")
    parser.add_argument("-u", "--url",  help="url to download")
    parser.add_argument("-s", "--show", help="Name of the show")
    args = parser.parse_args()
    config = load_configuration()
    networks = load_networks(config)
    urls = {urllib.parse.urlparse(config[key]['overview_url']).netloc: key for key in config.keys()}
    if args.url:
        url = urllib.parse.urlparse(args.url)
        if url.netloc in urls:
            networks[urls[url.netloc]][0].download_show(args.url)
    if args.network in networks.keys() and args.show:
        networks[args.network][0].download_show(networks[args.network][0].get_show_url(args.show))




