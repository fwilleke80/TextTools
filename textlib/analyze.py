#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import csv, json
import time, datetime
import operator
import string
from textlib import tokenize, readability, hashes, fileoperations


####################################
#
# Constants
#
####################################

# Analyze code version identifier
# Increase this at will, but note that it *has* to be increased
# if anything in the analysis or meta header generation changed!
ANALYZE_VERSION = '1.0.1'

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

def make_metadata_filename(filename):
    """From the .txt file's original filename & path,
    create the filename & path of the metadata .json file
    """
    fileBasePath = os.path.splitext(filename)[0]
    return os.path.join(fileBasePath + FILESUFFIX_JSON)

def make_wordtable_filename(filename):
    """From the .txt file's original filename & path,
    create the filename & path of the word count .csv table file
    """
    fileBasePath = os.path.splitext(filename)[0]
    return os.path.join(fileBasePath + FILESUFFIX_CSV)

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
    totalMaxPunctuationCountPerSentence = 0
    totalMaxPunctuationCountPerSentence_sentence = ''
    maxWordCountPerSentence = 0
    totalMaxSyllableCountPerWord = 0
    totalMaxSyllableCountPerWord_word = ''

    # Iterate sentences
    for sentence in textData['sentences']:

        # Total counters for whole sentence
        totalSyllableCountPerSentence = 0
        totalCharCountPerSentence = 0
        maxSyllableCountPerWord = 0
        maxSyllableCountPerWord_word = ''

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
            word['crc32'] = hashes.get_string_crc32(word['word'].encode('utf-8'))
            word['averageSyllableLength'] = round(float(charCount) / float(syllableCount), DIGITS)
            totalSyllableCountPerSentence += syllableCount
            # Sentence-local max syllable count
            if syllableCount > maxSyllableCountPerWord:
                maxSyllableCountPerWord = syllableCount
                maxSyllableCountPerWord_word = word['crc32']
            # Total max syllable count
            if syllableCount > totalMaxSyllableCountPerWord:
                totalMaxSyllableCountPerWord = syllableCount
                totalMaxSyllableCountPerWord_word = word['crc32']
            totalCharCountPerSentence += charCount

        # CRC32 checksum
        sentence['crc32'] = hashes.get_string_crc32(sentence['sentence'].encode('utf-8'))

        # Punctuation count
        punctuationCount = count_punctuation(sentence['sentence'])
        sentence['punctuationCount'] = punctuationCount
        if punctuationCount > totalMaxPunctuationCountPerSentence:
            totalMaxPunctuationCountPerSentence = punctuationCount
            totalMaxPunctuationCountPerSentence_sentence = sentence['crc32']
        totalPunctuationCountPerText += punctuationCount

        # Char count
        sentence['charCount'] = totalCharCountPerSentence

        # Word count
        wordCount = len(sentence['words'])
        sentence['wordCount'] = wordCount
        if wordCount > maxWordCountPerSentence:
            maxWordCountPerSentence = wordCount
            maxWordCountPerSentence_sentence = sentence['crc32']
        totalWordCountPerText += wordCount

        # Syllables
        sentence['averageSyllablesPerWord'] = round(float(totalSyllableCountPerSentence) / float(wordCount), DIGITS)
        sentence['averageSyllableLength'] = round(float(totalCharCountPerSentence) / float(totalSyllableCountPerSentence), DIGITS)
        totalSyllableCountPerText += totalSyllableCountPerSentence
        sentence['maxSyllableCountPerWord'] = { 'word' : maxSyllableCountPerWord_word, 'count' : maxSyllableCountPerWord }

        # Word length
        sentence['averageWordLength'] = round(float(totalCharCountPerSentence) / float(wordCount), DIGITS)
        totalCharCountPerText += totalCharCountPerSentence

    sentenceCount = len(textData['sentences'])
    textData['sentenceCount'] = sentenceCount
    textData['wordCount'] = totalWordCountPerText
    textData['charCount'] = totalCharCountPerText
    textData['punctuationCount'] = totalPunctuationCountPerText
    textData['maxPunctuationCountPerSentence'] = { 'sentence' : totalMaxPunctuationCountPerSentence_sentence, 'count' : totalMaxPunctuationCountPerSentence }
    textData['maxWordCountPerSentence'] = { 'sentence' : maxWordCountPerSentence_sentence, 'count' : maxWordCountPerSentence }
    textData['maxSyllableCountPerWord'] = { 'word' : totalMaxSyllableCountPerWord_word, 'count' : totalMaxSyllableCountPerWord }
    textData['averageWordsPerSentence'] = round(float(totalWordCountPerText) / float(sentenceCount), DIGITS)
    textData['averageSyllablesPerWord'] = round(float(totalSyllableCountPerText) / float(totalWordCountPerText), DIGITS)
    textData['averageSyllableLength'] = round(float(totalSyllableCountPerText) / float(totalCharCountPerText), DIGITS)
    textData['averageWordLength'] = round(float(totalCharCountPerText) / float(totalWordCountPerText), DIGITS)
    textData['averagePunctuationPerSentence'] = round(float(totalPunctuationCountPerText) / float(sentenceCount), DIGITS)

def metadata_header(filename, text, language):
    """Create header dataset with some basic info.
    """
    # Current date & time
    nowStr = get_datetime_now()

    meta = {
        'Filename' : fileoperations.shorten_filename(filename),
        'MD5' : hashes.get_file_md5(filename),
        'CRC32' : hashes.get_file_crc32(filename),
        'Date of analysis' : nowStr,
        'analyze_version' : ANALYZE_VERSION,
        'language' : language
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
    results = [
        { 'id' : 'words_with_6_letters', 'name' : 'Words with at least 6 letters' , 'value' : words_with_at_least_6_letters},
        { 'id' : 'words_with_at_least_3_syllables', 'name' : 'Words with at least 3 syllables' , 'value' : words_with_at_least_3_syllables},
        { 'id' : 'words_with_only_one_syllable', 'name' : 'Words with only one syllable' , 'value' : words_with_only_one_syllable},
        { 'id' : 'fre', 'name' : 'Flesch-Reading-Ease (DE)' , 'value' : round(fre, DIGITS)},
        { 'id' : 'frea', 'name' : 'Flesch-Reading-Ease (DE) Assessment' , 'value' : frea},
        { 'id' : 'fkgl', 'name' : 'Flesch-Kincaid Grade Level (US)' , 'value' : round(fkgl, DIGITS)},
        { 'id' : 'gfi', 'name' : 'Gunning-Fog Index (US)' , 'value' : round(gfi, DIGITS)},
        { 'id' : 'wsf1', 'name' : 'Erste Wiener Sachtextformel (DE)' , 'value' : round(wsf1, DIGITS)},
        { 'id' : 'wsf2', 'name' : 'Zweite Wiener Sachtextformel (DE)' , 'value' : round(wsf2, DIGITS)},
        { 'id' : 'wsf3', 'name' : 'Dritte Wiener Sachtextformel (DE)' , 'value' : round(wsf3, DIGITS)},
        { 'id' : 'wsf4', 'name' : 'Vierte Wiener Sachtextformel (DE)' , 'value' : round(wsf4, DIGITS)},
    ]
    return results


####################################
#
# Process / flow
#
####################################

def metadata_is_uptodate(filename, language):
    """Check header of .json file to find out if we need
    to analyze the referred text file again. This is done
    by checking the MD5 and CRC32 checksums in the header
    against freshly computed checksums of the file, and
    also checking the analyze_version in the header against
    the current one in the code.

    Return False if a fresh analysis is required, otherwise True
    """
    print('Checking ' + filename + '...')

    # Open metadata .json file
    metadataFilePath = make_metadata_filename(filename)
    try:
        metadata = fileoperations.load_json(metadataFilePath)['_meta']
    except:
        #print('Could not load metadata for ' + shorten_filename(filename) + '.')
        return False

    # Compute checksums for text file
    checksumCrc32 = hashes.get_file_crc32(filename)
    checksumMd5 = hashes.get_file_md5(filename)

    # Compare
    try:
        if metadata['CRC32'] != checksumCrc32:
            print('CRC32 differs: ' + metadata['CRC32'] + ' in metadata vs. ' + checksumCrc32 + ' from actual file.')
            return False
        if metadata['MD5'] != checksumMd5:
            print('MD5 differs: ' + metadata['MD5'] + ' in metadata vs. ' + checksumMd5 + ' from actual file.')
            return False
        if metadata['analyze_version'] != ANALYZE_VERSION:
            print('Analyze_version differs: ' + metadata['analyze_version'] + ' in metadata vs. ' + ANALYZE_VERSION + ' in program code.')
            return False
        if metadata['language'] != language:
            print('Language differs: ' + metadata['language'] + ' in metadata vs. current ' + language)
            return False
    except:
        print('Metadata header is missing or incomplete!')
        return False

    return True

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

# TODO
def merge_textdata(textData, globalTextData):
    """Merge textData into globalTextData,
    adding up to global data
    """
    print('Merging global textData dictionaries...')
    pass

def merge_wordtable(wordTable, globalWordTable):
    """Merge wordTable into globalWordTable,
    adding up to global data
    """
    # Iterate word table
    # Update counts
    print('Merging global wordTable dictionaries...')
    for word,valueDict in wordTable['words'].iteritems():
        wordCount = valueDict['count']

        newCount = int(globalWordTable.get(word, {}).get('count', 0) + wordCount)
        globalWordTable[word] = {
            'count' : newCount,
            'frequency' : float(0.0)
        }

    # Compute relative frequencies
    compute_wordfrequencies(globalWordTable)

def process_text(text, lang='de_DE'):
    """Perform all the analyses for a complete text
    Return textData and wordTable as a tuple
    """

    # Tokenize
    print('Tokenizing text...')
    textData = tokenize.tokenize_text(unicode(text), lang=lang)

    # Analyze
    print('Computing metadata...')
    compute_metadata(textData)
    wordTable = compute_word_table(textData)

    # Readability analysis
    print('Analyzing readability...')
    readingEase = compute_reading_ease_indices(textData)
    textData['readingEase'] = readingEase

    return (textData, wordTable)

def process_file(filePath, lang='de_DE'):
    """Load a file, process it, and write the result files
    """
    # Export paths
    metadataFilePath = make_metadata_filename(filePath)
    wordTableFilePath = make_wordtable_filename(filePath)
    print('Import text file : ' + filePath)
    print('Export metadata  : ' + metadataFilePath)
    print('Export word table: ' + wordTableFilePath)

    # Read text file
    print('Reading file...')
    text = fileoperations.read_text_file(filePath).decode('utf-8')

    # Process text file
    (textData, wordTable) = process_text(text, lang=lang)


    # Insert headers
    print('Inserting meta headers...')
    metaheader = metadata_header(filePath, text, language=lang)
    textData['_meta'] = metaheader
    wordTable['_meta'] = metaheader

    # Write result filea
    print('Writing JSON metadata file...')
    fileoperations.write_json(textData, metadataFilePath)
    print('Writing word count CSV table file...')
    write_csv(wordTable, wordTableFilePath)

    # Return data
    return (textData, wordTable)


def analyze(sourcePath, fileExtension='.txt', lang='de_DE', forceAnalyze=False):
    """Check filePath, start processing, measure processing time
    """
    print('Analyze version: ' + ANALYZE_VERSION)
    print('')

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
        process_file(sourcePath, lang=lang)
    elif os.path.isdir(sourcePath):
        # Tables for storing ALL data from ALL files
        # (to build global tables after processing the files)
        globalTextData = {}
        globalWordTable = {}

        # Process files in folder
        fileCount = 0
        filesInFolder = fileoperations.count_files(sourcePath, fileExtension)
        for file in os.listdir(sourcePath):
            if file.endswith(fileExtension):
                filename = os.path.join(sourcePath, file)
                # Check if we need to analyze this file
                if metadata_is_uptodate(filename, language=lang) and forceAnalyze == False:
                    # Metadata is up to date. Just load it and merge for the global table
                    print('Metadata is up to date. Skipping analysis.')

                    # Load existing metadata file and merge (to update global data)
                    textData = fileoperations.load_json(make_metadata_filename(filename))
                    merge_textdata(textData, globalTextData)
                    # TODO: Update global word table, too
                    # merge_wordtable(wordTable, globalWordTable)
                    # compute_wordfrequencies(globalWordTable)
                else:
                    # Metadata does not exist or is outdated. Analyze file.
                    print('Analyzing ' +
                          fileoperations.shorten_filename(filename) + '...')
                    (textData, wordTable) = process_file(filename, lang=lang)
                    merge_textdata(textData, globalTextData)
                    merge_wordtable(wordTable, globalWordTable)
                    compute_wordfrequencies(globalWordTable)
                    fileCount += 1
                print('')
        multiFileMsg = str(fileCount) + ' of ' + str(filesInFolder) + ' files '

        # Export paths
        if fileCount > 0:
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
            fileoperations.write_json(globalTextData, globalMetadataFilePath)
            print('Writing global word count CSV table file...')
            write_csv(finalGlobalWordTable, globalWordTableFilePath)
            print('')

    else:
        print('That is weird. It seems to be neither a file nor a folder...')

    print('Finished processing ' + multiFileMsg + '(' + str(round(time.time() - timeStart, 3)) + ' seconds)')
    print('')
