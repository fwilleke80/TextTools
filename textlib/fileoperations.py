#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json

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
