"""This module contains functions to work with link DB."""

import datetime

JISHO_URL = 'jisho.org/search/'


def _full_link(provider, word):
    """Return a website link for dictionary provider and word."""
    return 'http://' + provider + word


def create(conn, chat_id: str, word: str, provider: str = JISHO_URL) -> str:
    """Inserts new word in chat with id chat_id, returns link to inserted word."""
    if not chat_id:
        raise ValueError('chat_id is empty')
    if not word:
        raise ValueError('word is empty')
    if not provider:
        raise ValueError('provider is empty')

    now = datetime.datetime.utcnow().date()
    start_date = now - datetime.timedelta(days=now.weekday())  # Start of the current week — Monday.
    end_date = start_date + datetime.timedelta(days=6)  # End of the current week — Sunday.

    tx = conn.cursor()
    try:
        tx.execute(r'select id from links where word=%s and chat_id=%s and start_date <= %s and end_date >= %s;', (word, chat_id, start_date, end_date))
        row = tx.fetchone()
        if row:
            return row[0]

        tx.execute("""insert into links (chat_id, word, start_date, end_date, provider, clicks)
                             values (%s, %s, %s, %s, %s, 0)
                      returning id;""",
                   (chat_id, word, start_date, end_date, provider))
        new_id = tx.fetchone()[0]

        conn.commit()

        return new_id
    finally:
        tx.close()


# todo: Consider limiting clicks from one user somehow.
def handle_click(conn, link_id: int) -> str:
    """Increases click count for word with id link_id and returns full dictionary link to the word."""
    current_date = datetime.datetime.utcnow().date()

    tx = conn.cursor()
    try:
        tx.execute(r'select word, start_date, end_date, provider, clicks from links where id=%s;', (link_id,))
        row = tx.fetchone()
        if not row:
            raise ValueError('id "' + str(link_id) + '" is not found')

        word = row[0]
        start_date = row[1]
        end_date = row[2]
        provider = row[3]
        clicks = row[4]

        if start_date <= current_date <= end_date:
            tx.execute("""update links set clicks = %s where id = %s""", (clicks + 1, link_id))

        conn.commit()

        return _full_link(provider, word)
    finally:
        tx.close()


def get_words_with_clicks(conn, chat_id: str, current_date: datetime.date):
    """
    Returns top 5 most clicked words as pairs (word, clicks) for chat with chat_id
    and with start-end interval that includes current_date.
    """
    tx = conn.cursor()
    try:
        tx.execute("""select word, provider, clicks from links
                   where chat_id=%s and start_date <= %s and end_date >= %s
                   order by clicks desc
                   limit 5;""", (chat_id, current_date, current_date))

        words_with_clicks = []
        for row in tx.fetchall():
            words_with_clicks.append((_full_link(row[1], row[0]), row[2]))

        return words_with_clicks
    finally:
        tx.close()
