#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import operator
from textlib import analyze, fileoperations

####################################
#
# Constants
#
####################################

# Common Sense Matrix code version identifier
CSM_VERSION = '0.0.2'

CSM_MODES = ['help', 'learn', 'evaluate']

CSM_HELP = """An implementation of a Common Sense Matrix as developed by
Steffen Lepa and Frank Willeke in 2005.

--csm learn FOLDER
This will parse the metadata in a folder and create a common sense matrix of it.
This requires metadata to be present in that folder. Metadata can be created
using the --analyse option.

--csm evaluate MATRIXFILE ANALYZEFILE
This will use the Common Sense Matrix specified by the path MATRIXFILE and
evaluate a text file specified by the path ANALYZEFILE against it.

--csm help
Displays this help text.
"""

FILESUFFIX_RESULT = '_csm-results.csv'


def path_to_csm_filename(folderPath):
    return os.path.join(folderPath, "_" + os.path.basename(folderPath) + '_csm.json')


def wordtable_csv_to_worddata(wordTable):
    """Transform the rows of a word table to
    a Dict that associates words with their counts
    """
    wordBasedData = {}
    for word, wordCount in zip(wordTable['Word'], wordTable['Count']):
        # Take word and count value from CSV data
        wordBasedData[word] = {
            'count': wordCount#,
            #'frequency' : wordFrequency
        }
    return wordBasedData


def add_worddata(baseData, addData):
    """Merge two word data dicts, summing their values
    """
    for word, value in addData.iteritems():
        newCount = baseData.get(word, int(0)) + int(value['count'])
        baseData[word] = newCount


def worddata_to_sorted(wordData, descending=False):
    """
    """
    sortedList = sorted(wordData.items(), key=operator.itemgetter(1))
    return sortedList if not descending else list(reversed(sortedList))


def find_frequency_in_worddata(word, wordData):
    for wordPair in wordData:
        if wordPair[0].lower().encode("utf-8") == word.lower():
            return wordPair[2]
    return 0

def get_total_word_counts(wordData):
    uniqueWordCount = len(wordData)
    totalWordCount = 0
    for wordPair in wordData:
        totalWordCount += wordPair[1]
    return (totalWordCount, uniqueWordCount)

def calculate_word_frequencies(wordData, totalWordCount):
    resultList = []
    for wordPair in wordData:
        wordFrequency = float(wordPair[1]) / float(totalWordCount)
        resultList.append(list([wordPair[0], int(wordPair[1]), wordFrequency]))
    return resultList

def diff_worddata_tables(csmData, sortedEvalWordData):
    """
    """
    diffTable = []

    for wordPair in sortedEvalWordData:
        word = wordPair[0]
        wordFreq = wordPair[2]
        csmWordFreq = find_frequency_in_worddata(word, csmData)

        if wordFreq > csmWordFreq and csmWordFreq > 0.0:
            diffFreq = wordFreq - csmWordFreq
            #print word, wordFreq, " > ", csmWordFreq, " ==>> ", "{:0.4}".format(diffFreq)
            diffTable.append((word, diffFreq))

    diffTable.sort(key=operator.itemgetter(1))
    diffTable.reverse()

    return diffTable


class CommonSenseMatrix():
    """Common Sense Matrix implementation
    """

    def init(self):
        """Initialize the class
        Clears all knowledge.
        """
        self.learnedWords = None
        self.wordsToAnalyze = None
        self.resultTable = None

    
    def learn(self, sourceFolder):
        """
        """

        if not os.path.isdir(sourceFolder):
            print('ERROR: "' + sourceFolder + '" is not a valid folder!')
            return

        # Process files in folder
        fileCount = 0
        inputFileSuffix = '_wordfrequencies.csv'
        filesInFolder = fileoperations.count_files(sourceFolder, inputFileSuffix)
        if filesInFolder > 0:
            totalWordData = {}
            print('Learning from data in ' + sourceFolder + '...')
            for file in os.listdir(sourceFolder):
                if (not file.startswith('_')) and file.endswith(inputFileSuffix):
                    filename = os.path.join(sourceFolder, file)
                    # Open word table .csv file
                    try:
                        wordTable = fileoperations.load_csv(filename, delimiter=',', quotechar='"', firstColumnAsTitle=True, minimumRowLength=3)
                        print('Word data loaded from ' + filename)
                    except:
                        print('ERROR: Could not load word table from ' +
                            fileoperations.shorten_filename(filename) + '!')
                        return False

                    # Transform word table (row-based plain table) to word data (word-associated counts)
                    try:
                        wordData = wordtable_csv_to_worddata(wordTable)
                    except:
                        print('ERROR: Could not transform word table to word data!')
                        return False

                    # Merge word data of this file into totalWordData
                    try:
                        add_worddata(totalWordData, wordData)
                    except:
                        print('ERROR: Could not merge word data')
                        return False

                    fileCount += 1

            print('Learned from ' + str(fileCount) + ' of ' + str(filesInFolder) + ' files.')

            if fileCount > 0:
                # Transform totalWordData into data list, sorted descending by count
                try:
                    sortedWordData = worddata_to_sorted(totalWordData, descending=True)
                except:
                    print('ERROR: Could not sort word data!')
                    return False

                # Get total word counts
                (totalWordCount, uniqueWordCount) = get_total_word_counts(sortedWordData)
                print('Learned ' + str(totalWordCount) + ' words in total, ' + str(uniqueWordCount) + ' unique.')

                # Calculate word frequencies
                try:
                    finalWordData = calculate_word_frequencies(sortedWordData, totalWordCount)
                except:
                    print('ERROR: Could not calculate word frequencies!')
                    return False

                csmData = {}
                csmData['meta'] = {
                    'source' : sourceFolder,
                    'total_count': totalWordCount,
                    'unique_count' : uniqueWordCount
                }
                csmData['words'] = finalWordData

                # Store sortedWordData as JSON
                csmFilePath = path_to_csm_filename(sourceFolder)
                print('Writing Common Sense Matrix data to ' + csmFilePath + " ...")
                CommonSenseMatrix.write_csm(csmFilePath, csmData)
            else:
                print('STRANGE: Did not learn from any of the files.')
        else:
            print('No data found to learn from.')
            print('The folder must contain "*_wordfrequencies.csv" files generated with the "--analyze" option.')

        return True


    def evaluate(self, sourcePath, evalPath):
        """Evaluate CSM data by comparing word frequencies of an exemplary text against the frequencies from the CSM file
        """

        # Prepare source path
        if os.path.isdir(sourcePath):
            # It's a folder, guess the name of the CSM file
            csmFilename = path_to_csm_filename(sourcePath)
        elif os.path.isfile(sourcePath):
            # It's a file, just use the path
            csmFilename = sourcePath
        else:
            # Nothing found at that path
            print('ERROR: No Commons Sense Matrix data found at "' + sourcePath + '"')
            return False

        # Prepare evaluate path
        if os.path.isfile(evalPath):
            # It's a file, just use the path
            evalFilename = evalPath
        elif os.path.isdir(evalPath):
            # It's a folder, iterate possible files
            print('NOTE: Using a folder as evalPath not implemented yet!')
            return True
        else:
            # Nothing found at that path
            print('ERROR: Could not find ' + evalPath)
            return False

        # Load Common Sense Matrix data
        try:
            csmData = CommonSenseMatrix.read_csm(csmFilename)
            print('Common Sense Matrix data loaded from ' + csmFilename)
        except:
            print('ERROR: Could not load Common Sense Matrix from ' + csmFilename)
            return False

        # Open evaluate word table .csv file
        try:
            evalWordTable = fileoperations.load_csv(evalFilename, delimiter=',', quotechar='"', firstColumnAsTitle=True, minimumRowLength=3)
            print('Word data loaded from ' + evalFilename)
        except:
            print('ERROR: Could not load word table from ' + fileoperations.shorten_filename(evalFilename) + '!')
            return False

        print('Solving Common Sense Matrix...')

        # Transform word table (row-based plain table) to word data (word-associated counts)
        try:
            evalWordData = wordtable_csv_to_worddata(evalWordTable)
        except:
            print('ERROR: Could not transform word table to word data!')
            return False

        # Merge word data of this file into totalWordData
        finalEvalWordData = {}
        try:
            add_worddata(finalEvalWordData, evalWordData)
        except:
            print('ERROR: Could not merge word data')
            return False

        # Transform totalWordData into data list, sorted descending by count
        try:
            sortedFinalEvalWordData = worddata_to_sorted(finalEvalWordData, descending=True)
        except:
            print('ERROR: Could not sort word data!')
            return False

        # Get total word counts
        (totalWordCount, uniqueWordCount) = get_total_word_counts(sortedFinalEvalWordData)
        print('Learned ' + str(totalWordCount) + ' words in total, ' + str(uniqueWordCount) + ' unique.')

        try:
            sortedFinalEvalWordData = calculate_word_frequencies(sortedFinalEvalWordData, totalWordCount)
        except:
            print('ERROR: Could not calculate word frequencies for evaluate word data!')
            return False

        #try:
        resultTable = diff_worddata_tables(csmData['words'], sortedFinalEvalWordData)
        #except:
        #    print('ERROR: Could not diff CSM data against evaluation word data!')
        #    return False

        # Write resultTable
        csmResultFilename = os.path.splitext(evalPath)[0] + FILESUFFIX_RESULT
        wordRow = ''
        dataRow = ''
        try:
            with open(csmResultFilename, 'wb') as resultFile:
                for itemIndex, item in enumerate(resultTable):
                    wordRow = wordRow + (',' if itemIndex > 0 else '') + item[0]
                    dataRow = dataRow + (',' if itemIndex > 0 else '') + "{:0.6}".format(item[1])
                resultFile.write(wordRow + '\n')
                resultFile.write(dataRow + '\n')
            print('Saved result table to ' + csmResultFilename)
        except:
            print('ERROR: Could not write result table to ' + csmResultFilename + '!')

    #
    # Static members
    #

    @staticmethod
    def read_csm(filePath):
        """
        """
        return fileoperations.load_json(filePath)


    @staticmethod
    def write_csm(filePath, csm):
        """
        """
        fileoperations.write_json(csm, filePath)


def start(mode, args):
    print('Common Sense Matrix version ' + CSM_VERSION)
    print('')
    mode = mode.lower()
    if mode not in CSM_MODES:
        print('ERROR: Invalid MODE argument. Valid arguments are: ' + str(CSM_MODES))
        return
    if mode == 'help':
        print(CSM_HELP)
        return
    
    csm = CommonSenseMatrix()
    csm.init()
    if mode == 'learn':
        csm.learn(args[0])
        return
    elif mode == 'evaluate':
        csm.evaluate(args[0], args[1])
        return
