# Geoguessr Hack

![Geoguessr Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/GeoGuessr_logo.svg/1280px-GeoGuessr_logo.svg.png)

## Disclaimer

This project is for educational purposes only. I'm not responsible for your actions.

## Introduction

POC of a Geoguessr hack using a MITM proxy. It was made using Python 3.8 and [mitmproxy](https://mitmproxy.org/).

## Game Modes

### Standard

In **Standard** games, the full address will be printed and it opens in a new browser tab Google Maps at this address.

### Streak

In **US State Streak**, the state will be printed with the abbreviation (`Texas, TX`)

In **Country Streak**, the country name will be printed.

### Battle Royale

In **Battle Royale**, you get the same feedback as in **Standard** mode.

The difference with the other modes, is that you need to refresh the page when a new round starts.
The reason for that is that in unranked modes, the position of the current round is sent back by the server automatically when a new round starts.
When you play in **Battle Royale**, you do not get the location, probably by design. But when you refresh the page, it reconnects you to the game, and sends you the current round. Maybe assuming you got disconnected.

### Competitive City Streaks

In **Competitive City Streaks**, the full address will be printed. Unlike the rest of the game modes, information about the game are transmitted using WebSockets. We constantly receive requests but are interested in just the one received when the new round starts. As of now, it doesn't capture the first round you play.

### Response examples

Samples of the different responses sent back by the servers can be found in the folder `response-samples`.

## How to

```shell
# Installation of the project
git clone git@github.com:zetsumeishi/geoguessr-hack.git
cd geoguessr/
virtualenv -p python3.8 .venv
source .venv/bin/active
pip install -r requirements.txt
```

To use `mitmproxy`, you need to add to your browser the proxy server (`127.0.0.1:8080`). `mitmproxy` is used to intercept every request, include XHR.

Once it's done, the only thing left is to launch `mitmproxy` using the following command.

```shell
mitmdump --quiet -s geohack.py "~u geoguessr\.com" 2>error
```

To avoid receiving too many errors in the terminal, we redirect stderr output to a file. Goes for Python and `mitmproxy` errors. A better use of `mitmproxy` CLI options would remove unnecessary requests from being evaluated.
