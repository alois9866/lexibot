"""This module contains tests for model.py module."""
import datetime

import pytest
from pytest_postgresql import factories

import model

postgresql_proc = factories.postgresql_proc(port='5432')
postgresql_with_schema = factories.postgresql('postgresql_proc', load=['server/tf/scripts/create.sql'])


# noinspection PyShadowingNames,DuplicatedCode
def test_create(postgresql_with_schema):
    """Test create function."""
    with pytest.raises(ValueError):
        model.create(postgresql_with_schema, '', 'こんにちは')
    with pytest.raises(ValueError):
        model.create(postgresql_with_schema, 'dummy_chat_id', '')
    with pytest.raises(ValueError):
        model.create(postgresql_with_schema, 'dummy_chat_id', 'こんにちは', provider='')

    assert model.create(postgresql_with_schema, 'dummy_chat_id', 'こんにちは') == 1
    assert model.create(postgresql_with_schema, 'dummy_chat_id', '世界') == 2

    assert model.create(postgresql_with_schema, 'dummy_chat_id', '世界') == 2
    assert model.create(postgresql_with_schema, 'other_dummy_chat_id', '世界') == 3


# noinspection PyShadowingNames,DuplicatedCode
def test_handle_click(postgresql_with_schema):
    """Test handle_click function."""
    word = 'こんにちは'
    word_id = model.create(postgresql_with_schema, 'dummy_chat_id', word)

    with pytest.raises(ValueError):
        model.handle_click(postgresql_with_schema, int(word_id) + 1)  # ID does not exist.

    link = model.handle_click(postgresql_with_schema, int(word_id))
    assert link == model._full_link(model.JISHO_URL, word)

    cur = postgresql_with_schema.cursor()
    cur.execute(r'select word, clicks from links where id=%s;', (word_id,))
    row = cur.fetchone()
    assert row[0] == word
    assert row[1] == 1

    link = model.handle_click(postgresql_with_schema, int(word_id))
    assert link == model._full_link(model.JISHO_URL, word)

    cur = postgresql_with_schema.cursor()
    cur.execute(r'select word, clicks from links where id=%s;', (word_id,))
    row = cur.fetchone()
    assert row[0] == word
    assert row[1] == 2


# noinspection PyShadowingNames,DuplicatedCode
def test_get_words_with_clicks(postgresql_with_schema):
    """Test get_words_with_clicks function."""
    cur = postgresql_with_schema.cursor()
    cur.execute("""insert into links (id, chat_id, word, start_date, end_date, provider, clicks)
    values
    (1, 'dummy_chat_id', 'こんにちは', '2021-04-05', '2021-04-11', %s, 3),
    (2, 'dummy_chat_id', '世界', '2021-04-05', '2021-04-11', %s, 5),
    (3, 'dummy_chat_id', '日本語', '2021-04-05', '2021-04-11', %s, 9),
    (4, 'dummy_chat_id', '日本', '2021-03-29', '2021-04-04', %s, 1),
    (5, 'new_dummy_chat_id', '上手', '2021-04-05', '2021-04-11', %s, 20),
    (6, 'dummy_chat_id', '一', '2021-03-29', '2021-04-04', %s, 12),
    (7, 'dummy_chat_id', '二', '2021-04-05', '2021-04-11', %s, 1),
    (8, 'dummy_chat_id', '三', '2021-04-05', '2021-04-11', %s, 7)
    """, (model.JISHO_URL, model.JISHO_URL, model.JISHO_URL, model.JISHO_URL, model.JISHO_URL, model.JISHO_URL, model.JISHO_URL, model.JISHO_URL))

    # First day of the week.
    data = model.get_words_with_clicks(postgresql_with_schema, 'dummy_chat_id', datetime.datetime(year=2021, month=4, day=5).date())
    assert len(data) == 5
    assert data[0] == (model._full_link(model.JISHO_URL, '日本語'), 9)
    assert data[1] == (model._full_link(model.JISHO_URL, '三'), 7)
    assert data[2] == (model._full_link(model.JISHO_URL, '世界'), 5)
    assert data[3] == (model._full_link(model.JISHO_URL, 'こんにちは'), 3)
    assert data[4] == (model._full_link(model.JISHO_URL, '二'), 1)

    # Some day of the week.
    data = model.get_words_with_clicks(postgresql_with_schema, 'dummy_chat_id', datetime.datetime(year=2021, month=4, day=7).date())
    assert len(data) == 5
    assert data[0] == (model._full_link(model.JISHO_URL, '日本語'), 9)
    assert data[1] == (model._full_link(model.JISHO_URL, '三'), 7)
    assert data[2] == (model._full_link(model.JISHO_URL, '世界'), 5)
    assert data[3] == (model._full_link(model.JISHO_URL, 'こんにちは'), 3)
    assert data[4] == (model._full_link(model.JISHO_URL, '二'), 1)

    # Last day of the week.
    data = model.get_words_with_clicks(postgresql_with_schema, 'dummy_chat_id', datetime.datetime(year=2021, month=4, day=11).date())
    assert len(data) == 5
    assert data[0] == (model._full_link(model.JISHO_URL, '日本語'), 9)
    assert data[1] == (model._full_link(model.JISHO_URL, '三'), 7)
    assert data[2] == (model._full_link(model.JISHO_URL, '世界'), 5)
    assert data[3] == (model._full_link(model.JISHO_URL, 'こんにちは'), 3)
    assert data[4] == (model._full_link(model.JISHO_URL, '二'), 1)

    data = model.get_words_with_clicks(postgresql_with_schema, 'dummy_chat_id', datetime.datetime(year=2021, month=4, day=1).date())
    assert len(data) == 2
    assert data[0] == (model._full_link(model.JISHO_URL, '一'), 12)
    assert data[1] == (model._full_link(model.JISHO_URL, '日本'), 1)

    data = model.get_words_with_clicks(postgresql_with_schema, 'dummy_chat_id', datetime.datetime(year=2021, month=5, day=1).date())
    assert len(data) == 0

    data = model.get_words_with_clicks(postgresql_with_schema, 'new_dummy_chat_id', datetime.datetime(year=2021, month=4, day=7).date())
    assert len(data) == 1
    assert data[0] == (model._full_link(model.JISHO_URL, '上手'), 20)

    data = model.get_words_with_clicks(postgresql_with_schema, 'nonexistent_dummy_chat_id', datetime.datetime(year=2021, month=4, day=7).date())
    assert len(data) == 0
