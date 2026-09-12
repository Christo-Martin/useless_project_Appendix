import re
import random

VOWEL_GROUPS = re.compile(r'[aeiouyAEIOUY]+')

# Speech-like syllable building blocks
ONSETS = ['b', 'd', 'f', 'g', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'z',
          'bl', 'br', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sk', 'sp', 'st', 'tr']
VOWELS = ['a', 'e', 'i', 'o', 'u', 'ai', 'ee', 'oo', 'ou']
CODAS = ['', '', '', 'n', 'm', 's', 'k', 't', 'r', 'l']  # empty = open syllable more common


def count_syllables(word: str) -> int:
    """Rough heuristic: count vowel groups in a word."""
    word = word.lower().strip()
    word = re.sub(r'[^a-z]', '', word)  # strip punctuation
    if not word:
        return 1
    groups = VOWEL_GROUPS.findall(word)
    count = len(groups)

    # silent trailing 'e' (but not syllabic "-le" as in table/little/apple)
    if word.endswith('e') and not word.endswith('le') and count > 1:
        count -= 1

    # regular "-ed" past tense is usually silent (walked, used, hoped, blessed)
    # unless it follows a t/d sound, where it's a real syllable (wanted, started)
    if word.endswith('ed') and not word.endswith(('ted', 'ded')) and count > 1:
        count -= 1

    return max(1, count)


def make_syllable() -> str:
    onset = random.choice(ONSETS)
    vowel = random.choice(VOWELS)
    coda = random.choice(CODAS)
    return onset + vowel + coda


def make_gibberish_word(syllable_count: int) -> str:
    word = ''.join(make_syllable() for _ in range(syllable_count))
    return word.capitalize()


def gibberish_for_segment(text: str) -> str:
    """Given an original text segment, return a gibberish sentence
    with a matching per-word syllable count."""
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return "Mah."
    gibberish_words = [make_gibberish_word(count_syllables(w)) for w in words]
    sentence = ' '.join(gibberish_words)
    return sentence + '.'


if __name__ == '__main__':
    # quick manual test
    test_text = "Don't let artificial intelligence destroy your human instincts."
    print("Original:", test_text)
    print("Gibberish:", gibberish_for_segment(test_text))