# TVDownload
This application lets you download the latest episode of a show by name, or downloads an arbitrary episode if a url is given

## How to use
```
usage: tvdownloader.py [-h] [-n NETWORK] [-u URL] [-s SHOW]

optional arguments:
  -h, --help            show this help message and exit
  -n NETWORK, --network NETWORK
                        Network to download from
  -u URL, --url URL     url to download
  -s SHOW, --show SHOW  Name of the show
```
If the url option is used, the network option should not be provided. The application will figure out how to download.

## Provided networks
As of this moment, only 2 TV networks are supported:
* [Een](https://www.een.be)
* [Vier](http://www.vier.be)

One archive is supported as well:
* [VRTNu](https://www.vrt.be/vrtnu/)

Support for the other networks *should* be trivial.