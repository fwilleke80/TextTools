# TextTools
A command line tool, written in Python, that allows analyze a text, and generate metadata from it. That metadata is detailed attributes of the completely tokenised text: syllables, words, sentences and punctuation with their counts and frequencies, as well as reading ease assessments.

## Usage

`python texttool.py --analyze /Users/somebody/Desktop/some_text.txt`

## Results
The results will be written as companion files to the input file:

`/Users/somebody/Desktop/some_text_metadata.json`  
All metadata generated about the file.

`Users/somebody/Desktop/some_text_wordfrequencies.csv`  
A table with all words from the text, their absolute counts and relative frequencies.

## Note
Only plain text in ASCII oder UTF-8 is supported.

## Code dependencies
This project depends on the following Python packages, which can both be installed via PIP:

* PyHyphen
* NLTK,
