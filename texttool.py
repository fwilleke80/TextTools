#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
from textlib import analyze,csm


LANG_DEFAULT = 'de_DE'


def main():
    # Title
    print('TextTools 0.4.2')
    print('2019 by Frank Willeke')
    print(' ')

    # Command Line Options
    parser = optparse.OptionParser('usage: %prog --option1 arg1 arg2 --option2 arg')
    parser.add_option('-a', '--analyze', type='str', dest='analyze', nargs=1, default=None, metavar='PATH', help='Analyze a text and create extensive metadata')
    parser.add_option('-c', '--csm', type='str', dest='commonSense', nargs=1, default=None, metavar='MODE PATH', help='Learns or evaluates Common Sense Matrices. Use "--csm help" for more information.')
    parser.add_option('-l', '--language', type='str', dest='language', nargs=1, default='de_DE', metavar='ISOLANGUAGE', help='Define the language of the texts to analyze ("de_DE", "en_US", et cetera). If unspecified, "' + LANG_DEFAULT + '" is used.')
    (options, args) = parser.parse_args()

    # Text analysis
    if options.analyze:
        analyze.analyze(options.analyze, fileExtension='.txt', lang=options.language)
        return

    if options.commonSense:
        csm.start(options.commonSense, args)
        return

    parser.print_help()


# Kick off the shit...
if __name__=='__main__':
    try:
        print('')
        main()
        print('')
    except KeyboardInterrupt:
        print('Cancelled')
