#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import nltk
from hyphen import Hyphenator


hyphenator = Hyphenator('de_DE')


def is_alphanumeric(word):
    for char in word:
        if char.isalpha() == False:
            return False
    return True


# def trim_punctuation(word):
#     wordStr = str(word.encode('utf-8'))
#     while wordStr[:1] in string.punctuation:
#         wordStr = wordStr[1:]
#     while wordStr[-1:] in string.punctuation:
#         wordStr = wordStr[:-1]
#     return unicode(wordStr)


def tokenize_text(text):
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
        words = nltk.word_tokenize(sentence)

        # Iterate words
        for word in words:
            # Trim punctuation from beginning and end of word
            #word = trim_punctuation(word)

            # Ignore short "words" that do not contain alphanumerics
            if len(word) == 1 and not word[0].isalpha():
                continue

            # Ignore "words" that do not contain alphanumerics
            if is_alphanumeric(word) == False:
                continue

            # Split word into syllables
            syllables = hyphenator.syllables(word)

            # Word with only one syllable need special treatment,
            # because the hyphenator does not recognize them
            if len(syllables) == 0:
                syllables = [word]

            # Add to word data list
            wordData = {
                'word' : word,
                'syllables' : syllables
            }
            wordDataList.append(wordData)

        # print 'WordDataList:', wordDataList
        # print ''

        # Add to sentence dat list
        sentenceData = {
            'sentence' : sentence,
            'words' : wordDataList,
        }
        sentenceDataList.append(sentenceData)

    # print 'SentenceDataList:', sentenceDataList
    # print ''

    textData = {
        #'text' : text,
        'sentences' : sentenceDataList
    }

    return textData
