# TextTools
A command line tool, written in Python, that allows analyze a text, and generate metadata from it. That metadata is detailed attributes of the completely tokenised text: syllables, words, sentences and punctuation with their counts and frequencies, as well as reading ease assessments.

## Usage
### Analyze
This option will start an analysis of one or multiple text files. As a parameter, use either the full absolute path to a file or a folder.

`python texttool.py --analyze /Users/somebody/Desktop/texts/some_text.txt`  
`python texttool.py --analyze /Users/somebody/Desktop/texts/texts`

### Analyzed properties
The input text(s) will get the following treatments:

* **Tokenization**  
Texts will be split up into sentences, the sentences into words, and the words into syllables (hyphenization). All tokens will be included in the .json file.

* **Counts**  
Letters and syllables per word will be counted, as well as words per sentence, punctuation per sentence, and sentences per text. All counts will be included in the .json file.

* **Averages**  
Average letters per syllable over words, sentences, and text. Average syllables per word and sentence. Average word length per sentence and text. Average punctuation per sentence and text. Maximum punctuation count per sentence and text.

* **Readability indices** 
A number of readability indices are computed, too, from the created metadata. These include:

    * Words with at least 6 letters
    * Words with at least 3 syllables
    * Words with only 1 syllable
    * Flesch-Reading-Ease (DE) with assessment
    * Flesch-Kincaid Grade Level (US)
    * Gunning-Fog Index (US)
    * Wiener Sachtextformel (DE) (1st, 2nd, 3rd, 4th)

## Results
The results will be written as companion files to the input file(s):

`/Users/somebody/Desktop/texts/some_text_metadata.json`  
All metadata generated about the file.

`Users/somebody/Desktop/texts/some_text_wordfrequencies.csv`  
A table with all words from the text, their absolute counts and relative frequencies.

In addition to this, when analyzing a whole folder, summary files will be generated:  
`/Users/somebody/Desktop/texts/_texts_metadata.json`  
`/Users/somebody/Desktop/texts/_texts_wordfrequencies.csv`

## Note
Only plain text in ASCII oder UTF-8 is supported.

## Code dependencies
This project depends on the following Python packages, which can both be installed via PIP:

* PyHyphen
* NLTK
