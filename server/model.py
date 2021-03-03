"""This module contains functions to work with link DB."""

import datetime

JISHO_URL = 'jisho.org/word/'


def create(conn, chat_id: str, word: str, provider: str = JISHO_URL) -> int:
    """Inserts new word in chat with id chat_id, returns id of inserted word"""
    if len(chat_id) == 0:
        raise ValueError('chat_id is empty')
    if len(word) == 0:
        raise ValueError('word is empty')
    if len(provider) == 0:
        raise ValueError('provider is empty')

    start_date = datetime.datetime.utcnow().date()
    end_date = start_date + datetime.timedelta(weeks=1)

    tx = conn.cursor()

    # TODO: check if already exists for current time period.
    tx.execute("""insert into links (chat_id, word, start_date, end_date, provider, clicks)
                         values (%s, %s, %s, %s, %s, 0)
                  returning id;""",
               (chat_id, word, start_date, end_date, provider))
    new_id = tx.fetchone()[0]

    conn.commit()
    tx.close()

    return new_id


# todo: Consider limiting clicks from one user somehow.
def handle_click(conn, link_id: int) -> str:
    """Increases click count for word with id link_id and returns full dictionary link to the word."""
    current_date = datetime.datetime.utcnow().date()

    tx = conn.cursor()

    tx.execute(r'select word, start_date, end_date, provider, clicks from links where id=%s;', (link_id,))
    row = tx.fetchone()
    if row is None:
        raise ValueError('id "' + str(link_id) + '" is not found')
    word = row[0]
    start_date = row[1]
    end_date = row[2]
    provider = row[3]
    clicks = row[4]

    full_link = "http://" + provider + word

    if start_date <= current_date <= end_date:
        tx.execute("""update links set clicks = %s where id = %s""",
                   (clicks + 1, link_id))

    conn.commit()
    tx.close()

    return full_link  # todo: Use provider as template instead.


def get_words_with_clicks(conn, chat_id: str, start_date: datetime.date, end_date: datetime.date):
    """Returns top 5 most clicked words as pairs (word, clicks) for chat with chat_id with matching start and end dates."""
    tx = conn.cursor()

    tx.execute("""select word, clicks from links
               where chat_id=%s and start_date=%s and end_date=%s
               order by clicks desc
               limit 5;""", (chat_id, start_date, end_date))

    words_with_clicks = []
    for row in tx.fetchall():
        words_with_clicks.append((row[0], row[1]))

    tx.close()

    return words_with_clicks
