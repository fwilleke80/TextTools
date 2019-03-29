#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
from textlib import tokenize


###################
#
# Shuffling
#
###################

def switch_syllables(word1, word2, syllableIndex):
    tmpSyllable = word1['syllables'][syllableIndex]
    word1['syllables'][syllableIndex] = word2['syllables'][syllableIndex]
    word2['syllables'][syllableIndex] = tmpSyllable


def shuffletext(wordList, pattern):
    resultWordList = copy.deepcopy(wordList)
    for patternStep in pattern:
        word1 = resultWordList[0]
        word2 = resultWordList[1]

        switch_syllables(word1, word2, patternStep)

        resultWordList[0] = word1
        resultWordList[1] = word2

    return resultWordList


###################
#
# Reversing
#
###################

def reverse_word(word):
    result = unicode(word)[::-1]
    if word[0].isupper():
        result = result[0].upper() + result[1:-1] + result[-1].lower()
    return result


def reverse_string(s, byWord):
    if byWord:
        words = tokenize.tokenize_sentence_to_words(s)
        result = ''
        for word in words:
            result = result + reverse_word(word) + ' '
        return result

    else:
        return s[::-1]


###################
#
# General
#
###################

def assemble_text(wordList):
    text = ''
    for word in wordList:
        for syllable in word['syllables']:
            text = text + syllable
        text = text + ' '
    return text


def have_fun(text, lang='de_DE'):
    wordList = []
    text = text.decode('utf-8')
    words = tokenize.tokenize_sentence_to_words(text)
    for word in words:
        syllables = tokenize.tokenize_word_to_syllables(word, lang=lang)
        wordData = {
            'word' : word,
            'syllables' : syllables
        }
        wordList.append(wordData)

    print('')
    print(text)
    print(reverse_string(text, byWord=True))
    print(assemble_text(shuffletext(wordList, [0])))
    print(assemble_text(shuffletext(wordList, [-1])))
    print(assemble_text(shuffletext(wordList, [0, -1])))
