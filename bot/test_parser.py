"""This module contains tests for parser.py"""
from bot.parser import is_japanese_char, extract_japanese_words


def test_is_japanese_char():
    '''test parser.is_japanese_char'''
    assert is_japanese_char('ラ') # katakana
    assert is_japanese_char('ㇹ') # katakana phonetic extension
    assert is_japanese_char('ﾈ') # halfwidth katakana
    assert is_japanese_char('え') # hiragana
    assert is_japanese_char('国') # cjk
    assert not is_japanese_char('t')
    assert not is_japanese_char('Б')

def test_extract_japanese_words():
    '''test parser.extract_japanese_words'''
    assert extract_japanese_words("you have to あなたの運命を証明する your destiny") == \
           ['あなた', 'の', '運命', 'を', '証明', 'する']
    assert extract_japanese_words("Симуляция 0 シミュレーションシュミレーション Симуляция 3!") == \
           ['シミュレーション', 'シュミレーション']
    assert extract_japanese_words("При вет др4жище!!") == []
    assert extract_japanese_words("Of the thighs and thighs -> すもももももももものうち") == \
        ['すもも', 'も', 'もも', 'も', 'もも', 'の', 'うち']
    assert extract_japanese_words("国家公務員") == ['国家', '公務員']
