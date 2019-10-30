#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import optparse
from textlib import analyze,csm,fun


LANG_DEFAULT = 'de_DE'


def main():
    # Title
    print('TextTools 0.4.2')
    print('2019 by Frank Willeke')
    print(' ')

    # Command Line Options
    parser = optparse.OptionParser('usage: %prog --option1 arg1 arg2 --option2 arg')
    parser.add_option('-a', '--analyze', action='store_true', dest='analyze', default=None,
                      help='Analyze a text and create extensive metadata')
    parser.add_option('-l', '--language', type='str', dest='language', nargs=1, default='de_DE', metavar='ISOLANGUAGE',
                      help='Define the language of the texts to analyze ("de_DE", "en_US", et cetera). If unspecified, "' + LANG_DEFAULT + '" is used.')
    parser.add_option('-c', '--csm', type='str', dest='commonSense', nargs=1, default=None, metavar='MODE PATH',
                      help='Learns or evaluates Common Sense Matrices. Use "--csm help" for more information.')
    parser.add_option('-s', '--shuffle', type='str', dest='fun',
                      nargs=1, default=None, metavar='FUN', help='Fun with words')
    parser.add_option('-f', '--force', action='store_true', dest='force', default=False, help='Force update of cached data')
    (options, args) = parser.parse_args()

    # Memorize start time
    timeStarted = time.time()

    # Text analysis
    doneSomething = False
    if options.analyze:
        analyze.analyze(args[0], fileExtension='.txt', lang=options.language, forceAnalyze=options.force)
        doneSomething = True

    # Common Sense Matrix
    if options.commonSense:
        csm.start(options.commonSense, args)
        doneSomething = True
        
    # Word Shuffle Fun
    if options.fun:
        fun.have_fun(options.fun, lang=options.language)
        doneSomething = True

    if not doneSomething:
        parser.print_help()
    else:
        print('\nRuntime: ' + "{:.3f}".format(time.time() - timeStarted) + ' seconds.')


# Kick off the shit...
if __name__=='__main__':
    try:
        print('')
        main()
        print('')
    except KeyboardInterrupt:
        print('Cancelled')
