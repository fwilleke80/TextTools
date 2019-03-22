#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import csv, json
import time, datetime
import string
import hashlib
from textlib import tokenize


####################################
#
# Constants
#
####################################

FILESUFFIX_JSON = '_meta.json'
FILESUFFIX_CSV = '_wordfrequencies.csv'
DIGITS = 5


####################################
#
# Standard functions
#
####################################

def read_text_file(filePath):
    """Read text file as raw binary file,
    and return contents.
    """

    with open(filePath, 'rb') as textFile:
        text = textFile.read()
    return text

def write_json(data, filename):
    jsonData = json.dumps(data, indent=4, sort_keys=True)
    with open(filename, 'wb') as jsonFile:
        jsonFile.write(jsonData)

def write_csv(data, filename):
    # Prepare DSV rows
    headerRows = [['Filename'],['Date of Analysis'],['MD5 hash']]
    dataRows = [['Word'],['Count'],['Frequency']]

    headerRows[0].append(data['_meta']['filename'])
    headerRows[1].append(data['_meta']['dateOfAnalysis'])
    headerRows[2].append(data['_meta']['md5'])

    for k,v in data['words'].iteritems():
        dataRows[0].append(k.encode('utf-8'))
        dataRows[1].append(round(v[0], DIGITS))
        dataRows[2].append(round(v[1], DIGITS))

    # Begin writing
    with open(filename, 'wb') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvWriter.writerows(headerRows)
        csvWriter.writerow([])
        csvWriter.writerows(dataRows)


####################################
#
# Analysis
#
####################################

def count_punctuation(sentence):
    count = lambda l1, l2: len(list(filter(lambda c: c in l2, l1)))
    return count(sentence, string.punctuation)

def compute_metadata(textData):
    """Parse textData dictionary and compute the additional metadata.
    The resulting metadata will be inserted into the dictionary.
    """

    # Total counters for whole text
    totalSyllableCountPerText = 0
    totalWordCountPerText = 0
    totalCharCountPerText = 0
    totalPunctuationCountPerText = 0

    # Iterate sentences
    for sentence in textData['sentences']:

        # Total counters for whole sentence
        totalSyllableCountPerSentence = 0
        totalCharCountPerSentence = 0

        # Iterate words
        for word in sentence['words']:

            # Iterate syllables
            # for syllable in word['syllables']:
            #     pass

            # Compute data
            syllableCount = len(word['syllables'])
            charCount = len(word['word'])
            word['syllableCount'] = syllableCount
            word['charCount'] = charCount
            word['averageSyllableLength'] = round(float(charCount) / float(syllableCount), DIGITS)
            totalSyllableCountPerSentence += syllableCount
            totalCharCountPerSentence += charCount

        # Punctuation count
        punctuationCount = count_punctuation(sentence['sentence'])
        sentence['punctuationCount'] = punctuationCount
        totalPunctuationCountPerText += punctuationCount

        # Char count
        sentence['charCount'] = totalCharCountPerSentence

        # Word count
        wordCount = len(sentence['words'])
        sentence['wordCount'] = wordCount
        totalWordCountPerText += wordCount

        # Syllables
        sentence['averageSyllablesPerWord'] = round(float(totalSyllableCountPerSentence) / float(wordCount), DIGITS)
        sentence['averageSyllableLength'] = round(float(totalCharCountPerSentence) / float(totalSyllableCountPerSentence), DIGITS)
        totalSyllableCountPerText += totalSyllableCountPerSentence

        # Word length
        sentence['averageWordLength'] = round(float(totalCharCountPerSentence) / float(wordCount), DIGITS)
        totalCharCountPerText += totalCharCountPerSentence

    sentenceCount = len(textData['sentences'])
    textData['sentenceCount'] = sentenceCount
    textData['wordCount'] = totalWordCountPerText
    textData['charCount'] = totalCharCountPerText
    textData['punctuationCount'] = totalPunctuationCountPerText
    textData['averageWordsPerSentence'] = round(float(totalWordCountPerText) / float(sentenceCount), DIGITS)
    textData['averageSyllablesPerWord'] = round(float(totalSyllableCountPerText) / float(totalWordCountPerText), DIGITS)
    textData['averageSyllableLength'] = round(float(totalSyllableCountPerText) / float(totalCharCountPerText), DIGITS)
    textData['averageWordLength'] = round(float(totalCharCountPerText) / float(totalWordCountPerText), DIGITS)
    textData['averagePunctuationPerSentence'] = round(float(totalPunctuationCountPerText) / float(sentenceCount), DIGITS)

def metadata_header(filename, text):
    # Hash
    #txt = text.encode('ascii', errors='ignore')
    md5 = hashlib.md5()
    md5Input = text.encode('utf-8')
    md5.update(md5Input)

    # Current date & time
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y-%m-%d %H:%M")

    meta = {
        'filename' : filename,
        'md5' : md5.hexdigest(),
        'dateOfAnalysis' : nowStr
    }

    return meta

def compute_word_table(textData):
    wordTable = {}

    # Iterate sentences
    for sentence in textData['sentences']:
        # Iterate words in sentence
        for word in sentence['words']:
            # Make word lower-case
            wordStr = word['word'].lower()
            # Update word count in table
            wordTable[wordStr] = wordTable.get(wordStr, 0) + 1

    # Calculate relative word frequencies
    wordCount = textData['wordCount']
    for key, value in wordTable.iteritems():
        # Value is now a tuple with the value and the relative value
        wordTable[key] = (value, float(value) / float(wordCount))

    resultTable = {
        'words' : wordTable,
    }

    return resultTable


####################################
#
# Readability / Reading Ease indices
#
####################################

# Flesch-Reading-Eass Index (DE)
def compute_flesch_reading_ease(asl, asw):
    return 180.0 - asl - (58.5 * asw)

# Flasch-Reading-Ease Assessment
def assess_flesch_reading_ease(fre):
    if fre < 0.0:
        return 'Invalid FRE index'
    elif fre <= 30.0:
        return 'very difficult'
    elif fre <= 50.0:
        return 'difficult'
    elif fre <= 60.0:
        return 'medium difficult'
    elif fre <= 70.0:
        return 'medium'
    elif fre <= 80.0:
        return 'medium easy'
    elif fre <= 90.0:
        return 'easy'
    elif fre <= 100.0:
        return 'very easy'

# Flesch-Kincaid Grade Level (US)
def compute_flesch_kincaid_grade_level(asl, asw):
    return (0.39 * asl) + (11.8 * asw) - 15.59

# Gunning-Fog Index (US)
def compute_gunning_fog_index(w, s, d):
    return ((w / s) + d) * 0.4

# Wiener Sachtextformel (DE)
def compute_wiener_sachtextformel(MS, SL, IW, ES):
    wstf1 = 0.1935 * MS + 0.1672 * SL + 0.1297 * IW - 0.0327 * ES - 0.875
    wstf2 = 0.2007 * MS + 0.1682 * SL + 0.1373 * IW - 2.779
    wstf3 = 0.2963 * MS + 0.1905 * SL - 1.1144
    wstf4 = 0.2656 * SL + 0.2744 * MS - 1.693
    return (wstf1, wstf2, wstf3, wstf4)

def compute_reading_ease_indices(textData):
    DIGITS = 5

    # Input data
    wordCount = textData['wordCount']
    sentenceCount = textData['sentenceCount']
    asl = textData['averageWordsPerSentence']
    asw = textData['averageSyllablesPerWord']

    # Count words with special properties
    words_with_at_least_6_letters = 0
    words_with_at_least_3_syllables = 0
    words_with_only_one_syllable = 0
    for sentence in textData['sentences']:
        for word in sentence['words']:
            # Words with at least 6 letters
            if word['charCount'] >= 6:
                words_with_at_least_6_letters += 1
            # Words with at least 3 syllables
            syllableCount = word['syllableCount']
            if syllableCount >= 3:
                words_with_at_least_3_syllables += 1
            # Words with only one syllable
            if syllableCount == 1:
                words_with_only_one_syllable += 1

    # Compute Flesch-Reading-Ease
    fre = compute_flesch_reading_ease(asl=asl, asw=asw)
    frea = assess_flesch_reading_ease(fre)

    # Flesch-Kincaid Grade Level
    fkgl = compute_flesch_kincaid_grade_level(asl=asl, asw=asw)

    # Compute Gunning-Fog Index
    gfi = compute_gunning_fog_index(w=wordCount, s=sentenceCount, d=words_with_at_least_3_syllables)

    # Compute Wiener Sachtextformel
    ms = (wordCount / words_with_at_least_3_syllables) if words_with_at_least_3_syllables != 0 else 0.0
    iw = (wordCount / words_with_at_least_6_letters) if words_with_at_least_6_letters != 0 else 0.0
    es = (wordCount / words_with_only_one_syllable) if words_with_only_one_syllable != 0 else 0.0
    (wsf1, wsf2, wsf3, wsf4) = compute_wiener_sachtextformel(MS=ms, SL=asl, IW=iw, ES=es)

    # All results go into the dict
    resultDict = {
        'Words with at least 6 letters' : words_with_at_least_6_letters,
        'Words with at least 3 syllables' : words_with_at_least_3_syllables,
        'Words with only one syllable' : words_with_only_one_syllable,
        'Flesch-Reading-Ease (DE)' : round(fre, DIGITS),
        'Flesch-Reading-Ease (DE) Assessment' : frea,
        'Flesch-Kincaid Grade Level (US)' : round(fkgl, DIGITS),
        'Gunning-Fog Index (US)' : round(gfi, DIGITS),
        'Erste Wiener Sachtextformel (DE)' : round(wsf1, DIGITS),
        'Zweite Wiener Sachtextformel (DE)' : round(wsf2, DIGITS),
        'Dritte Wiener Sachtextformel (DE)' : round(wsf3, DIGITS),
        'Vierte Wiener Sachtextformel (DE)' : round(wsf4, DIGITS),
    }

    return resultDict


####################################
#
# Process / flow
#
####################################

def process_text(text):
    """Perform all the analyses for a complete text
    Return textData and wordTable as a tuple
    """

    # Tokenize
    print('Tokenizing text...')
    textData = tokenize.tokenize_text(unicode(text))

    # Analyze
    print('Computing metadata...')
    compute_metadata(textData)
    wordTable = compute_word_table(textData)

    # Readability analysis
    print('Analyzing readability...')
    readingEase = compute_reading_ease_indices(textData)
    textData['readingEase'] = readingEase

    return (textData, wordTable)

def process_file(filePath):
    """Load a file, process it, and write the result files
    """

    # Check input file
    if not os.path.isfile(filePath):
        sys.exit('ERROR: "' + filePath + '" is not the path of an existing file!')

    # Export paths
    fileBasePath = os.path.splitext(filePath)[0]
    metadataFilePath = os.path.join(fileBasePath + FILESUFFIX_JSON)
    wordTableFilePath = os.path.join(fileBasePath + FILESUFFIX_CSV)
    print('Import text file : ' + filePath)
    print('Export metadata  : ' + metadataFilePath)
    print('Export word table: ' + wordTableFilePath)
    print('')

    # Read text file
    print('Reading file...')
    text = read_text_file(filePath).decode('utf-8')

    # Process text file
    (textData, wordTable) = process_text(text)


    # Insert headers
    print('Inserting meta headers...')
    metaheader = metadata_header(filePath, text)
    textData['_meta'] = metaheader
    wordTable['_meta'] = metaheader

    # Write result filea
    print('Writing JSON metadata file...')
    write_json(textData, metadataFilePath)
    print('Writing word count CSV table file...')
    write_csv(wordTable, wordTableFilePath)

def analyze(filePath):
    # Check args
    if filePath is None or len(filePath) == 0:
        sys.exit('ERROR: No path to text file provided!')

    # Memorize start time
    timeStart = time.time()

    # Process the file, including all analyses and result data export
    process_file(filePath)

    print('')
    print('Finished (' + str(round(time.time() - timeStart, 3)) + ' seconds)')
