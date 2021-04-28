"""This is a module with text parsing methods."""

import re
from typing import List

from sudachipy import dictionary as japanese_dictionary
from sudachipy import tokenizer as japanese_tokenizer

unicode_ranges = {
    'hiragana': range(int("0x3040", base=16), int("0x309f", base=16)),
    'katakana': range(int("0x30a0", base=16), int("0x30ff", base=16)),
    'katakana_phonetic_extensions': range(int("0x31f0", base=16), int("0x31ff", base=16)),
    'halfwidth_katakana': range(int("0xff65", base=16), int("0xff9f", base=16)),
    'cjk': range(int("0x4e00", base=16), int("0x9faf", base=16))
}


def is_japanese_char(symbol: str) -> bool:
    """Test whether character can be found in japanese text according to Unicode code."""
    keys = ['hiragana', 'katakana', 'katakana_phonetic_extensions', 'halfwidth_katakana', 'cjk']
    for k in keys:
        if ord(symbol) in unicode_ranges[k]:
            return True
    return False


def extract_japanese_words(message: str) -> List[str]:
    """Each non-japanese word is skipped. Japanese words are extracted.

    Japanese text has no whitespaces, that's why tokenization is required
    """
    regexp = r"[\w\-']+"
    words = list(filter(lambda w: is_japanese_char(w[0]), re.findall(regexp, message)))
    tokenizer_mode = japanese_tokenizer.Tokenizer.SplitMode.B
    tokenizer = japanese_dictionary.Dictionary().create()
    japanese_words = []
    for word in words:
        tokens = [to.surface() for to in tokenizer.tokenize(word, tokenizer_mode)]
        japanese_words.extend(tokens)
    return japanese_words
