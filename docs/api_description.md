# Server API Description

### Create link.

POST `http://<SERVER_IP>/create`

Input: JSON object:

```json
{
  "chat_id": "<ID of chat where the bot is running>",
  "word": "<single japanese word>",
  "token_hash": "<SHA-256 hash of Telegram bot token>"
}
```

This call will create a new record for word `word` and chat `chat_id`. It returns a number: ID for a link to get the
word, as described below. If the word already exists in the current time period and chat, an existing link will be
returned.

### Click link.

GET `http://<SERVER_IP>/i/<id>`

Input:

`<id>`: unique ID of a previously created word.

If word with ID <id> exists, increases click count for it by one. Redirects to the dictionary page for the word.

### Get top words for given time period.

GET `http://<SERVER_IP>/top/<chat_id>[?date=<date>]`

Input:

`<chat_id>`: ID of chat for which the statistics should be calculated.

`date`: optional, date in `%Y-%m-%d` format.

This call will return a list of pairs (dictionary link, click count) for top __5__ words in the given chat during the
time period, that includes the specified date. If the date is not specified, current date will be used.
