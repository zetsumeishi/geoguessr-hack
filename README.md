# Geoguessr Hack

![Geoguessr Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/GeoGuessr_logo.svg/1280px-GeoGuessr_logo.svg.png)

## Disclaimer

This project is for educational purposes only. I'm not responsible for your actions.

## Introduction

This simple program will print in the terminal the exact location of every coordinates given by the game. It also works in multiplayer.

POC of a Geoguessr hack using a MITM proxy. It was made using Python 3.11 and [mitmproxy](https://mitmproxy.org/). MITM Proxy supports WSL if you are on Windows and use WSL.

## How to

```shell
# Installation of the project
git clone git@github.com:zetsumeishi/geoguessr-hack.git
cd geoguessr-hack/
virtualenv -p python3.11 .venv
source .venv/bin/active
pip install -r requirements.txt
```

To configure `mitmproxy` in your browser, refer to the [documentation](https://docs.mitmproxy.org/stable/overview-getting-started/). `mitmproxy` is used to intercept every request.

Once it's done, the only thing left is to launch `mitmproxy` using the following command.

```shell
mitmdump --quiet -s "geohack.py"
```

Once you connect to Geoguessr using the same browser you configured the proxy on, you can start any type of game and the detailed address will be printed in the terminal before every round.
