#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json, csv

####################################
#
# File operations
#
####################################

def count_files(path, extension):
    """Count files in a folder that match a certain file extension
    """
    count = 0
    for file in os.listdir(path):
        if file.endswith(extension):
            count += 1
    return count


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


def load_json(filename):
    """Loads a JSON file
    """
    with open(filename, 'rb') as jsonFile:
        return json.load(jsonFile)


def write_json(data, filename):
    """Export data as structured JSON file
    """
    jsonData = json.dumps(data, indent=4, sort_keys=True)
    with open(filename, 'wb') as jsonFile:
        jsonFile.write(jsonData)


def load_csv(filename, delimiter=',', quotechar='"', firstColumnAsTitle=True, minimumRowLength=3):
    """
    """
    with open(filename, 'rb') as csvFile:
        csvReader = csv.reader(csvFile, delimiter=delimiter, quotechar=quotechar)

        if firstColumnAsTitle:
            # Use first field of each row as key for a dictionary
            # Put rest of rows into dictionary values, filtered by minimumRowLength
            csvData = {}
            for row in csvReader:
                if minimumRowLength > 0 and len(row) < minimumRowLength:
                    continue
                csvData[row[0]] = row[1:]
            return csvData

        else:
            # Simply read rows, filtered by minimumRowLength
            # Return as list of rows
            csvData = [row for row in csvReader if (minimumRowLength == 0 or len(row) >= minimumRowLength)]
            return csvData
