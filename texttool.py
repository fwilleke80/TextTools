#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
from textlib import analyze


def main():
    # Title
    print('TextTools 0.4')
    print('2019 by Frank Willeke')
    print(' ')

    # Command Line Options
    parser = optparse.OptionParser('usage: %prog --option1 arg1 arg2 --option2 arg')
    parser.add_option('--analyze', type='str', dest='analyze', nargs=1, default=None, metavar='PATH', help='Analyze a text and create extensive metadata.')
    (options, args) = parser.parse_args()

    # Text analysis
    if options.analyze:
        analyze.analyze(options.analyze, fileExtension='.txt')
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
