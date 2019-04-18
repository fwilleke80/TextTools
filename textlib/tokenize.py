#!/usr/bin/python
# -*- coding: utf-8 -*-
import nltk
from hyphen import Hyphenator


# Hyphenator class instance
# Lazy-initialized in tokenize_text()
hyphenator = None


def is_alphanumeric(s):
    """Return False if there are any non-alphanumeric
    characters in the given string. Otherwise return True.
    """
    for c in s:
        if c.isalpha() == False:
            return False
    return True


def tokenize_sentence_to_words(sentence):
    return nltk.word_tokenize(sentence)


def tokenize_word_to_syllables(word, lang):
    global hyphenator
    if hyphenator is None:
        print('Initializing Hyphenator (' + lang + ')...')
        hyphenator = Hyphenator(lang)

    syllables = hyphenator.syllables(word)

    # Word with only one syllable need special treatment,
    # because the hyphenator does not recognize them
    if len(syllables) == 0:
        syllables = [word]

    return syllables


def tokenize_text(text, lang='de_DE'):
    """Tokenize an entire text.

    The text will be split into sentences.
    Sentences will be split into words.
    Words will be split into syllables.

    Returns a dictionary containing a list with all sentences in the text.
    Each "sentence" element contains the original sentence, and a list with all words in the sentence.
    Each "word" element contains the original word, and a list with all syllables in the word.
    """

    # List of data sets for each sentence in this text
    sentenceDataList = []

    # Split text into list of sentences
    sentences = nltk.sent_tokenize(text)

    # Iterate sentences
    for sentence in sentences:
        # List of data sets for each word in this sentence
        wordDataList = []

        # Split sentence into list of words
        words = tokenize_sentence_to_words(sentence)

        # Iterate words
        for word in words:
            # Ignore short "words" that do not contain alphanumerics
            if len(word) == 1 and not word[0].isalpha():
                continue

            # Ignore "words" that do not contain alphanumerics
            if is_alphanumeric(word) == False:
                continue

            # Split word into syllables
            syllables = tokenize_word_to_syllables(word, lang=lang)

            # Add to word data list
            wordData = {
                'word' : word,
                'syllables' : syllables
            }
            wordDataList.append(wordData)

        # Add to sentence dat list
        sentenceData = {
            'sentence' : sentence,
            'words' : wordDataList,
        }
        sentenceDataList.append(sentenceData)

    textData = {
        'sentences' : sentenceDataList
    }

    return textData
