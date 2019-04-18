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
CSM_VERSION = '0.0.1'

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


def wordtable_csv_to_worddata(wordTable):
    """Transform the rows of a word table to
    a Dict that associates words with their counts
    """
    wordBasedData = {}
    for word, wordCount, wordFrequency in zip(wordTable['Word'], wordTable['Count'], wordTable['Frequency']):
        wordBasedData[word] = {
            'count': wordCount#,
            #'frequency' : wordFrequency
        }
    return wordBasedData


def add_worddata(baseData, addData):
    """Merge two word data dicts, summing their values
    """
    for word, value in addData.iteritems():
        newCount = baseData.get(word, 0) + int(value['count'])
        baseData[word] = newCount


def worddata_to_sorted(wordData, descending=False):
    sortedList = sorted(wordData.items(), key=operator.itemgetter(1))
    return sortedList if not descending else list(reversed(sortedList))


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

    
    def evaluate(self, args):
        """
        """
        pass


    def learn(self, args):
        """
        """
        sourceFolder = args[0]

        if not os.path.isdir(sourceFolder):
            print('ERROR: "' + sourceFolder + '" is not a valid folder!')
            return

        # Process files in folder
        fileCount = 0
        inputFileSuffix = '_wordfrequencies.csv'
        filesInFolder = fileoperations.count_files(sourceFolder, inputFileSuffix)
        totalWordData = {}
        print('Learning from data in ' + sourceFolder + '...')
        for file in os.listdir(sourceFolder):
            if (not file.startswith('_')) and file.endswith(inputFileSuffix):
                filename = os.path.join(sourceFolder, file)
                # Open word table .csv file
                try:
                    wordTable = fileoperations.load_csv(filename, delimiter=',', quotechar='"', firstColumnAsTitle=True, minimumRowLength=3)
                except:
                    print('ERROR: Could not load word table from ' +
                          fileoperations.shorten_filename(filename) + '!')
                    return False
                try:
                    wordData = wordtable_csv_to_worddata(wordTable)
                except:
                    print('ERROR: Could not transform word table to word data!')
                    return False
                try:
                    add_worddata(totalWordData, wordData)
                except:
                    print('ERROR: Could not merge word data')
                    return False
                #print(str(wordData))
                #print('')
                print('Word table loaded from ' + filename)
        try:
            sortedWordData = worddata_to_sorted(totalWordData, descending=True)
        except:
            print('ERROR: Could not sort word data!')
            return False
        print('')
        print(str(sortedWordData))

        # Store sortedWordData as JSON
        fileoperations.write_json(sortedWordData, os.path.join(sourceFolder, "_" + os.path.basename(sourceFolder) + '_csm.json'))

        return True

    #
    # Static members
    #

    @staticmethod
    def read_csm(filePath):
        """
        """
        pass

    @staticmethod
    def write_csm(filePath, csm):
        """
        """
        pass


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
        csm.learn(args)
        return
    elif mode == 'evaluate':
        csm.evaluate(args)
        return
