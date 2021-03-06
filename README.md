# TextTools
A command line tool, written in Python, that allows analyze a text, and generate metadata from it. That metadata is detailed attributes of the completely tokenised text: syllables, words, sentences and punctuation with their counts and frequencies, as well as reading ease assessments.

## Usage
General:  
`python texttool.py PATH --option1 --option2 argument`

Examples:  
`python texttool.py /Users/somebody/Desktop/texts --analyze --force --csm learn`  
  This will force (re-)analysis of the folder and then start a Common Sense Matrix learn session.

### Analyze
This option will start an analysis of one or multiple text files. As a parameter, use either the full absolute path to a file or a folder.

`python texttool.py /Users/somebody/Desktop/texts/some_text.txt --analyze`  
`python texttool.py /Users/somebody/Desktop/texts --analyze`

#### Analyzed properties
The input text(s) will get the following treatments:

* **Tokenization**  
Texts will be split up into sentences, the sentences into words, and the words into syllables (hyphenization). All tokens will be included in the .json file. Tokenization is language-dependent.

  *Note: The first time a language is used, the hyphenator will download the relevant corpora from the internet. Data stored by PyHyphen and NLTK can add up to around 400 MB per language, depending on quality of support.*

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

### Common Sense Matrix
Blah, blah, blah

#### What is it?
Blah, blah, blah

#### How is it used?
Blah, blah, blah

##### Learn
Blah, blah, blah

##### Evaluate
Blah, blah, blah

### Fun
A fun module to play around with words. Currently, it only does some test stuff.

Call it like this:  
`python texttool.py --fun "Schimmelkäse Brummbär"`

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
