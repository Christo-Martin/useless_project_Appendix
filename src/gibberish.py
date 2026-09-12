import re
import random

VOWEL_GROUPS = re.compile(r'[aeiouyAEIOUY]+')

# Speech-like syllable building blocks
ONSETS = ['b', 'd', 'f', 'g', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'z',
          'bl', 'br', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sk', 'sp', 'st', 'tr']
VOWELS = ['a', 'e', 'i', 'o', 'u', 'ai', 'ee', 'oo', 'ou']
CODAS = ['', '', '', 'n', 'm', 's', 'k', 't', 'r', 'l']  # empty = open syllable more common

# Level 1: consonant-preserving near-homophones (keep first letter, swap vowel)
NEAR_VOWELS = {'a': 'e', 'e': 'i', 'i': 'o', 'o': 'u', 'u': 'a'}

# Level 4 & 5: extended noisy phoneme pools
NOISY_ONSETS = ONSETS + ['ch', 'sh', 'th', 'wh', 'ph', 'kn', 'wr', 'qu']
NOISY_VOWELS = VOWELS + ['ue', 'ea', 'ie', 'oa', 'au', 'aw']


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


def make_gibberish_word(syllable_count: int, level: int = 3) -> str:
    """Build a fake word with `syllable_count` syllables.

    Level 4-5 use a noisier phoneme pool for wilder sounds.
    """
    pool_onsets = NOISY_ONSETS if level >= 4 else ONSETS
    pool_vowels = NOISY_VOWELS if level >= 4 else VOWELS
    parts = []
    for _ in range(syllable_count):
        onset = random.choice(pool_onsets)
        vowel = random.choice(pool_vowels)
        coda  = random.choice(CODAS)
        parts.append(onset + vowel + coda)
    return ''.join(parts).capitalize()


def _near_homophone_word(word: str) -> str:
    """Level 1: swap each vowel for the 'next' vowel — keeps shape recognisable."""
    result = []
    for ch in word.lower():
        if ch in NEAR_VOWELS:
            result.append(NEAR_VOWELS[ch])
        else:
            result.append(ch)
    return ''.join(result).capitalize()


def _partial_gibberish_word(word: str, level: int) -> str:
    """Level 2-3: keep first letter, replace remaining syllables."""
    n_syl = count_syllables(word)
    first = word[0].lower()
    rest_syls = max(1, n_syl - 1)
    # Level 2 uses the same onset pool as the word start
    # Level 3 is fully random
    suffix = ''.join(
        random.choice(ONSETS) + random.choice(VOWELS) + random.choice(CODAS)
        for _ in range(rest_syls)
    )
    return (first + suffix).capitalize()


def gibberish_for_segment(text: str, level: int = 3) -> str:
    """Given an original text segment, return a gibberish string.

    Args:
        text:  Original transcribed text for the segment.
        level: Meaning-destruction level 1-5.
            1 = near-homophones  (barely confusing)
            2 = first-letter-preserved partial gibberish
            3 = syllable-matched full gibberish  [default]
            4 = syllable-matched, noisier phonemes
            5 = syllable count ±1, wildest phoneme pool
    """
    words = re.findall(r"[A-Za-z']+", text)
    if not words:
        return "Mah."

    gibberish_words = []
    for w in words:
        n = count_syllables(w)
        if level == 1:
            gibberish_words.append(_near_homophone_word(w))
        elif level == 2:
            gibberish_words.append(_partial_gibberish_word(w, level))
        elif level == 3:
            gibberish_words.append(make_gibberish_word(n, level=3))
        elif level == 4:
            gibberish_words.append(make_gibberish_word(n, level=4))
        else:  # level 5 — add or drop a syllable randomly
            n_noisy = max(1, n + random.choice([-1, 0, 0, 1]))
            gibberish_words.append(make_gibberish_word(n_noisy, level=5))

    sentence = ' '.join(gibberish_words)
    return sentence + '.'


if __name__ == '__main__':
    # quick manual test
    test_text = "Don't let artificial intelligence destroy your human instincts."
    print("Original:", test_text)
    print("Gibberish:", gibberish_for_segment(test_text))