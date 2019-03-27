#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import csv, json
import time, datetime
import operator
import string
from textlib import tokenize,readability,filehash


####################################
#
# Constants
#
####################################

# Suffix added to metadata filenames
FILESUFFIX_JSON = '_metadata.json'

# Suffix added to word table filenames
FILESUFFIX_CSV = '_wordfrequencies.csv'

# Decimal places for rounding any float values in files
DIGITS = 5


####################################
#
# Standard functions
#
####################################

def get_datetime_now(dtFormat = '%Y-%m-%d %H:%M'):
    now = datetime.datetime.now()
    return now.strftime(dtFormat)


####################################
#
# File operations
#
####################################

def shorten_filename(full_path):
    """Takes a path and returns only the
    last part of it (e.g. name of the file)
    """
    return os.path.basename(full_path)

def read_text_file(filePath):
    """Read text file as raw binary file,
    and return contents.
    """
    with open(filePath, 'rb') as textFile:
        text = textFile.read()
    return text

def write_json(data, filename):
    """Export data as structured JSON file
    """
    jsonData = json.dumps(data, indent=4, sort_keys=True)
    with open(filename, 'wb') as jsonFile:
        jsonFile.write(jsonData)

def write_csv(data, filename):
    """Export data as CSV file
    """
    # Fill meta rows
    headerRows = []
    try:
        headerRows.append(['Filename', data['_meta']['Filename']])
    except:
        pass
    try:
        headerRows.append(['Folder', data['_meta']['Folder']])
    except:
        pass
    try:
        headerRows.append(['Date of Analysis', data['_meta']['Date of analysis']])
    except:
        pass
    try:
        headerRows.append(['CRC32 Checksum', data['_meta']['CRC32']])
    except:
        pass
    try:
        headerRows.append(['MD5 Hash', data['_meta']['MD5']])
    except:
        pass

    # Fill data rows
    dataRows = [['Word'], ['Count'], ['Frequency']]
    for dataSet in sorted(data['words'].items(), key=operator.itemgetter(1), reverse=True):
        dataRows[0].append(dataSet[0].encode('utf-8'))
        wordData = dataSet[1]

        dataRows[1].append(int(wordData['count']))
        dataRows[2].append(round(wordData['frequency'], DIGITS))


    # Write file
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
    """Count number of punctuation characters in a string.
    """
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
    maxPunctuationCountPerSentence = 0

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
        maxPunctuationCountPerSentence = max(maxPunctuationCountPerSentence, punctuationCount)
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
    textData['maxPunctuationCountPerSentence'] = maxPunctuationCountPerSentence
    textData['averageWordsPerSentence'] = round(float(totalWordCountPerText) / float(sentenceCount), DIGITS)
    textData['averageSyllablesPerWord'] = round(float(totalSyllableCountPerText) / float(totalWordCountPerText), DIGITS)
    textData['averageSyllableLength'] = round(float(totalSyllableCountPerText) / float(totalCharCountPerText), DIGITS)
    textData['averageWordLength'] = round(float(totalCharCountPerText) / float(totalWordCountPerText), DIGITS)
    textData['averagePunctuationPerSentence'] = round(float(totalPunctuationCountPerText) / float(sentenceCount), DIGITS)

def metadata_header(filename, text):
    """Create header dataset with some basic info.
    """
    # Current date & time
    nowStr = get_datetime_now()

    meta = {
        'Filename' : shorten_filename(filename),
        'MD5' : filehash.get_file_md5(filename),
        'CRC32' : filehash.get_file_crc32(filename),
        'Date of analysis' : nowStr
    }

    return meta

def compute_word_table(textData):
    """Traverse textData dictionary and compute a table
    with occurring words, their absolute quanitities and
    their relative frequencies.
    """
    wordTable = {}

    # Iterate sentences
    for sentence in textData['sentences']:
        # Iterate words in sentence
        for word in sentence['words']:
            # Make word lower-case
            wordStr = word['word'].lower()
            # Update word count in table
            count = wordTable.get(wordStr, {}).get('count', 0)
            wordTable[wordStr] = {
                'count' : int(count + 1),
                'frequency' : float(0.0)
            }

    # Calculate relative word frequencies
    totalWordCount = textData['wordCount']
    for key, valueDict in wordTable.iteritems():
        # Value is now a tuple with the value and the relative value
        # TODO: Use child Dict, not a stupid Tuple!
        #       That will also make the CSV export easier!
        #wordTable[key] = (value, float(value) / float(wordCount))
        count = valueDict['count']
        wordTable[key] = {
            'count' : count,
            'frequency' : float(count) / float(totalWordCount)
        }

    resultTable = {
        'words' : wordTable,
    }

    return resultTable


####################################
#
# Readability
#
####################################

def compute_reading_ease_indices(textData):
    """Traverse textData and compute all
    readability / reading ease indices.
    """
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
    fre = readability.compute_flesch_reading_ease(asl=asl, asw=asw)
    frea = readability.assess_flesch_reading_ease(fre)

    # Flesch-Kincaid Grade Level
    fkgl = readability.compute_flesch_kincaid_grade_level(asl=asl, asw=asw)

    # Compute Gunning-Fog Index
    gfi = readability.compute_gunning_fog_index(w=wordCount, s=sentenceCount, d=words_with_at_least_3_syllables)

    # Compute Wiener Sachtextformel
    ms = (wordCount / words_with_at_least_3_syllables) if words_with_at_least_3_syllables != 0 else 0.0
    iw = (wordCount / words_with_at_least_6_letters) if words_with_at_least_6_letters != 0 else 0.0
    es = (wordCount / words_with_only_one_syllable) if words_with_only_one_syllable != 0 else 0.0
    (wsf1, wsf2, wsf3, wsf4) = readability.compute_wiener_sachtextformel(MS=ms, SL=asl, IW=iw, ES=es)

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

# TODO
def merge_textdata(textData, globalTextData):
    """Merge textData into globalTextData,
    adding up to global data
    """
    pass

# TODO
def merge_wordtable(wordTable, globalWordTable):
    """Merge wordTable into globalWordTable,
    adding up to global data
    """
    # Iterate word table
    # Update counts
    for word,valueDict in wordTable['words'].iteritems():
        wordCount = valueDict['count']

        newCount = int(globalWordTable.get(word, {}).get('count', 0) + wordCount)
        globalWordTable[word] = {
            'count' : newCount,
            'frequency' : float(0.0)
        }

    # Compute relative frequencies
    compute_wordfrequencies(globalWordTable)


# TODO
def compute_wordfrequencies(wordTable):
    """Compute relative frequencies in an existing word table
    """
    # First get total word count
    totalWordCount = 0
    for word, valueDict in wordTable.iteritems():
        totalWordCount += valueDict.get('count', 0)

    for word, valueDict in wordTable.iteritems():
        count = valueDict['count']
        wordTable[word] = {
            'count' : count,
            'frequency' : float(count) / float(totalWordCount)
        }


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
    # Export paths
    fileBasePath = os.path.splitext(filePath)[0]
    metadataFilePath = os.path.join(fileBasePath + FILESUFFIX_JSON)
    wordTableFilePath = os.path.join(fileBasePath + FILESUFFIX_CSV)
    print('Import text file : ' + filePath)
    print('Export metadata  : ' + metadataFilePath)
    print('Export word table: ' + wordTableFilePath)

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
    print('')

    # Return data
    return (textData, wordTable)


def analyze(sourcePath, fileExtension='.txt'):
    """Check filePath, start processing, measure processing time
    """
    # Check file path
    if sourcePath is None or len(sourcePath) == 0:
        sys.exit('ERROR: No path to text file provided!')
    if not os.path.exists(sourcePath):
        sys.exit('ERROR: "' + sourcePath + '" is not the path of an existing file or folder!')

    # Memorize start time
    timeStart = time.time()

    # Start processing
    multiFileMsg = ''
    if os.path.isfile(sourcePath):
        # Process single file
        process_file(sourcePath)
    elif os.path.isdir(sourcePath):
        # Tables for storing ALL data from ALL files
        # (to build global tables after processing the files)
        globalTextData = {}
        globalWordTable = {}

        # Process files in folder
        fileCount = 0
        for file in os.listdir(sourcePath):
            if file.endswith(fileExtension):
                (textData, wordTable) = process_file(os.path.join(sourcePath, file))
                merge_textdata(textData, globalTextData)
                merge_wordtable(wordTable, globalWordTable)
                compute_wordfrequencies(globalWordTable)
                fileCount += 1
        multiFileMsg = str(fileCount) + ' files '

        # Export paths
        print('Building global tables...')
        absPath = os.path.normpath(os.path.abspath(sourcePath))
        pathName = os.path.basename(absPath)
        globalMetadataFilePath = os.path.join(absPath, '_' + pathName + FILESUFFIX_JSON)
        globalWordTableFilePath = os.path.join(absPath, '_' + pathName + FILESUFFIX_CSV)
        print('Export global metadata  : ' + globalMetadataFilePath)
        print('Export global word table: ' + globalWordTableFilePath)

        finalGlobalWordTable = {
            '_meta' : {
                'Folder' : absPath,
                'Date of analysis' : get_datetime_now()
            },
            'words' : globalWordTable
        }

        # Write result files
        print('Writing global JSON metadata file...')
        write_json(globalTextData, globalMetadataFilePath)
        print('Writing global word count CSV table file...')
        write_csv(finalGlobalWordTable, globalWordTableFilePath)
        print('')

    else:
        print('That is weird. It seems to be neither a file nor a folder...')

    print('Finished processing ' + multiFileMsg + '(' + str(round(time.time() - timeStart, 3)) + ' seconds)')
    print('')
