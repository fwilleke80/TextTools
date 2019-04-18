#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy
import json
from textlib import tokenize


###################
#
# String operations
#
###################

def find_nth(string, searchStr, n):
    parts = string.split(searchStr, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(searchStr)

def find_nth_vowel(string, n, lastIfNotEnough=False):
    # TOTO: n < 0 does not work correctly yet
    vowels = u'aeiouäöü'

    foundVowels = 0
    foundAt = -1

    # Start at string beginning, forward
    if n >= 0:
        for i,c in enumerate(string):
            if c in vowels:
                if foundVowels == n:
                    return i
                foundVowels += 1
                foundAt = i

    # Start at string end, backward
    else:
        #print 'searching backwards'
        searchIn = string[::-1]
        #print searchIn
        for i,c in enumerate(searchIn):
            if c in vowels:
                foundVowels += 1
                if foundVowels == abs(n):
                    #print i
                    return len(searchIn) - (i + 1)
                foundAt = len(searchIn) - (i + 1)


    if foundVowels > 0 and lastIfNotEnough:
        return foundAt

    return -1

def set_char(string, char, index):
    #print string, char, index
    #print string[:index], char, string[index+1:]
    return string[:index] + char + string[index+1:]


###################
#
# Shuffling vowels
#
###################

def switch_vowels(word1, word2, vowelIndex):
    index1 = find_nth_vowel(word1, vowelIndex, lastIfNotEnough=True)
    index2 = find_nth_vowel(word2, vowelIndex, lastIfNotEnough=True)
    #print index1, word1[index1]
    #print index2, word2[index2]
    if index1 > -1 and index2 > -1:
        result = set_char(word1, word2[index2], index1), set_char(word2, word1[index1], index2)
        #print result
    else:
        result = (word1, word2)
    return result

def shuffle_vowels(wordList, pattern):
    resultWordList = copy.deepcopy(wordList)
    for patternStep in pattern:
        word1 = resultWordList[0]['word']
        word2 = resultWordList[1]['word']

        result = switch_vowels(word1, word2, patternStep)

        resultWordList[0]['word'] = result[0]
        resultWordList[1]['word'] = result[1]

    return resultWordList


###################
#
# Shuffling consonants (and consonant groups like "ch" and "sch" and "ck" et cetera)
#
###################

# TODO



###################
#
# Shuffling syllables
#
###################

def switch_syllables(word1, word2, syllableIndex):
    tmpSyllable = word1['syllables'][syllableIndex]
    word1['syllables'][syllableIndex] = word2['syllables'][syllableIndex]
    word2['syllables'][syllableIndex] = tmpSyllable

def shuffle_syllables(wordList, pattern):
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

def reverse_string(s, byWord=True):
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

def pattern_actions_to_string(pattern):
# TODO
    string = ''
    for item in pattern['items']:
        if item['action'] == 'reverse':
            actionStr = 'R'
        elif item['action'] == 'shuffle_syllables':
            actionStr = 'SS('
        elif item['action'] == 'shuffle_vowels':
            actionStr = 'SV('

        for p in item.get('pattern', []):
            actionStr = actionStr + str(p) + ','

        actionStr = actionStr[:-1] + ')'
        string = string + actionStr + ','
    return string


def load_json(filename):
    with open(filename, 'rb') as jsonFile:
        return json.load(jsonFile)

def assemble_text(wordList, bySyllables):
    text = ''
    for word in wordList:
        if bySyllables:
            for syllable in word['syllables']:
                text = text + syllable
        else:
            text = text + word['word']
        text = text + ' '
    return text

def sentence_to_wordlist(sentence, lang):
    wordList = []
    words = tokenize.tokenize_sentence_to_words(sentence)
    for word in words:
        syllables = tokenize.tokenize_word_to_syllables(word, lang=lang)
        wordData = {
            'word' : word,
            'syllables' : syllables
        }
        wordList.append(wordData)
    return wordList

def have_fun(sentence, lang='de_DE'):
    sentence = sentence.decode('utf-8')
    print(sentence)

    patternList = load_json(filename='./funpatterns.json')
    for pattern in patternList:
        wordList = sentence_to_wordlist(sentence, lang=lang)
        print('')
        print('Pattern: ' + pattern['name'] + ' (' + pattern_actions_to_string(pattern) + ')')
        for patternItem in pattern['items']:
            action = patternItem['action']
            if action == 'reverse':
                resultStr = reverse_string(sentence, byWord=True)
            elif action == 'shuffle_syllables':
                resultStr = assemble_text(shuffle_syllables(wordList, patternItem['pattern']), bySyllables=True)
            elif action == 'shuffle_vowels':
                resultStr = assemble_text(shuffle_vowels(wordList, patternItem['pattern']), bySyllables=False)
            wordList = sentence_to_wordlist(resultStr, lang=lang)
        print(resultStr)
