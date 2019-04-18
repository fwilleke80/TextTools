#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
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
        filesInFolder = fileoperations.count_files(sourceFolder, '.txt')
        print('Learning from data in ' + sourceFolder + '...')
        for file in os.listdir(sourceFolder):
            if (not file.startswith('_')) and  file.endswith('_metadata.json'):
                filename = os.path.join(sourceFolder, file)
                # Open metadata .json file
                try:
                    metadata = fileoperations.load_json(filename)['_meta']
                except:
                    print('Could not load metadata from ' + fileoperations.shorten_filename(filename) + '.')
                    return False
                print('Metadata loaded from ' + filename)

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