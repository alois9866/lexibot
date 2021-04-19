# lexibot

Simple Telegram bot for language learning support.

## Description

`lexibot` is a client/server application that provides functionality to read Telegram blogs while simultaniously learning all the foreign words used.
For now we consider only one foreign language: Japanese.
The client bot application will be a participant of a Telegram channel along with an administrator.
When the administrator shares some information with potential readers of the channel, the bot processes them and provides these features:
* List all the Japanese words in a message along with a clickable link to online dictionary for every word.
* Regularly write out a statistical report on what words are clicked the most in the channel during a set period of time.

## Roadmap

1. Plan the implementation:
    - Client bot application based on [telegram API python wrapper](https://github.com/python-telegram-bot/python-telegram-bot).
    - Database to store words and related information.
    - A server which provides links to online dictionary and statistical reports to the client.
      API details [here](docs/api_description.md).

2. Set up local database and server.

3. Implement request processing and database entry updates on the server side.

4. Implement compilation of statistical reports from the database.

5. Provide a way to set up and deploy everything to AWS.

6. Implement bot client's features:
- channel message parsing;
- link creation;
- channel replies (links to online dictionary, statistical report on the most clickable words).

## _How to_ section

### Preliminaries

In order to try anything firstly install
required python packages (we suggest using virtual environment):
```shell script
pip install -r requirements.txt
```
Also prepare json configuration file with the following format:
```json
{
    "token": "<provide_your_token_here>",
    "server": {
        "ip": "<ip>",
        "port": "<port>"
    }
}
```


### Run a local server

You will need a valid docker installation to run the database for the local server. If you want to configure the
database manually, see TODO.

1. Set server `ip` to 0.0.0.0 and `port` to 80 in config file.
1. In order to prepare a database for lexibot server, execute `make run-local-db`
1. To run a local server, execute `make run-local-server CONFIG_PATH=<path_to_config_file>`
1. After you are done working with the local server, execute `make stop-local-db` to stop and destroy the database

### Run a local bot client

```
python -m bot.main -cp <path_to_config_file>
```
Set additional `-v` flag, if you want to see debugging logs.

### Run a server in the cloud

TODO

### Run a bot client in the cloud

TODO

### Generate local HTML documentation

Make sure you have [Sphinx](https://www.sphinx-doc.org) package installed.
Execute `make doc_html` and open _docs/doc_build/html/index.html_
in a browser.
