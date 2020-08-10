"""
Authors: Matthew Ivler and Chris Nardi
Takes a directory of documents and creates and creates an version where all text files within the directory
have ngrams (bi-, tri-, tetra- grams) for common collections of words. This ngramming helps with topic modeling.
"""

import glob
import regex
import csv
from multiprocessing import Pool
import sys
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

path = "/data/annual_reports_tesseract/*.txt"
freq_min = 24000
processors = 25
stops = set(stopwords.words("english"))

csv.field_size_limit(sys.maxsize)
text_files = glob.glob(path)

word_fd = nltk.FreqDist()


def element_clean(gram):
    """
    Makes sure to eliminate ngrams that are composed of stopwords
    :param gram: tuple- tuple of strings representing a bigram of words from a document
    :return: str- the gram is returned if it is an acceptable gram
    """
    if gram[0] in stops or gram[1] in stops:
        return ""
    elif len(gram[0].split("_")) == 2:
        bigram_split = gram[0].split("_")
        if bigram_split[0] in stops:
            return ""
    else:
        return gram


def unigrams(filename):
    """
    Creates a dictionary of all unigrams and their frequency in a file..
    :param filename: str- the file whose unigram frequency is being counted
    :return: FreqDist- a set of key value pairs where the keys are unigrams and the value is the unigram frequency
    """
    with open(filename, encoding="utf-8") as f:
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
    return nltk.FreqDist([token.lower() for token in tokens])


# Efficient run to get full corpus frequency distribution of unigrams
unipool = Pool(processors)
unigram_dists = unipool.map(unigrams, text_files)
for freqdist in unigram_dists:
    word_fd.update(freqdist)
unipool.close()
unipool.join()

# Only keeps the most frequent unigrams
word_fd_frequent = set([word for word, count in word_fd.items() if count >= freq_min])

# Avoid memory errors
del unigram_dists
del word_fd

#Initialization and progress marker
bigram_fd = nltk.FreqDist()
print("Unigrams complete")


def bigrams(filename):
    """
    See unigrams function, but pretend it says bigrams this time.
    """
    with open(filename, encoding="utf-8") as f:
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
        bigrams = nltk.bigrams(token.lower() for token in tokens)
        bigrams_filtered = [bigram for bigram in bigrams if bigram[0] in word_fd_frequent and bigram[1] in word_fd_frequent]
    del bigrams
    bigrams_cleaned = [bigram for bigram in bigrams_filtered if element_clean(bigram) != ""]
    del bigrams_filtered
    return nltk.FreqDist(bigrams_cleaned)


# Efficient creatio nof bigram frequency distribution
bipool = Pool(processors)
bigram_dists = bipool.map(bigrams, text_files)
for freqdist in bigram_dists:
    bigram_fd.update(freqdist)
bipool.close()
bipool.join()

# Gives metadata about bigrams and counts to help determine at what cutoff to create bigrams
with open("bigrams_count.txt", "w", encoding="utf-8") as out:
    for word, count in bigram_fd.items():
        bigram = word[0] + "_" + word[1]
        line = bigram + " " + str(count) + "\n"
        out.write(line)

# Only keeps the frequent bigrams
bigram_fd_frequent = set([word for word, count in bigram_fd.items() if count >= freq_min])
del bigram_dists
del bigram_fd

# Save space
del word_fd_frequent

# Progress checkpoint
print("bigram complete")

bigram_trigram_fd = nltk.FreqDist()


def trigrams(filename):
    """
    See Unigrams but replace it with trigrams.
    """
    with open(filename, encoding="utf-8") as f:
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
        tokens = [token.lower() for token in tokens]

        # Actually creates bigrams out in order to judge if form tri- and tetragrams
        updated_tokens = []
        previous_token = None
        for token in tokens:
            if previous_token and (previous_token, token) in bigram_fd_frequent:
                token = previous_token + '_' + token
                updated_tokens[-1] = token
            else:
                updated_tokens.append(token)
            previous_token = token

        del tokens
        bigrams = nltk.bigrams(token.lower() for token in updated_tokens)
        del updated_tokens
        bigrams_cleaned_of_stopwords = [bigram for bigram in bigrams if element_clean(bigram) != ""]
        del bigrams
    new_temp_fd = nltk.FreqDist(bigrams_cleaned_of_stopwords)
    del bigrams_cleaned_of_stopwords
    return new_temp_fd


# Efficient creation of tri/tetragram frequency distribution
tripool = Pool(20)
trigram_dists = tripool.map(trigrams, text_files)
for freqdist in trigram_dists:
    bigram_trigram_fd.update(freqdist)
del trigram_dists
tripool.close()
tripool.join()

# Progress check because memory allocation typically becomes an issue during the trigram multiprocessing
print("trigrams almost done")

# Metadata on trigram counts
with open("trigrams_count.txt", "w", encoding="utf-8") as out:
    for word, count in bigram_trigram_fd.items():
        trigram = word[0] + "_" + word[1]
        line = trigram + " " + str(count) + "\n"
        out.write(line)

bigram_trigram_fd_frequent = set([word for word, count in bigram_trigram_fd.items() if count >= freq_min])
del bigram_trigram_fd

print("trigrams complete\nwriting...")


def filewriter(filename):
    """
    Creates bigrams and trigrams based on which are necessary, and writes a text file based on them
    :param filename: str- Name of file being converted
    :return: None
    """
    with open(filename, encoding="utf-8") as f:
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
        tokens = [token.lower() for token in tokens]

        updated_tokens = []
        previous_token = None
        for token in tokens:
            if previous_token and (previous_token, token) in bigram_fd_frequent:
                token = previous_token + '_' + token
                updated_tokens[-1] = token
            else:
                updated_tokens.append(token)
            previous_token = token

        updated_tokens_tri = []
        previous_token = None
        for token in updated_tokens:
            if previous_token and (previous_token, token) in bigram_trigram_fd_frequent:
                token = previous_token + '_' + token
                updated_tokens_tri[-1] = token
            else:
                updated_tokens_tri.append(token)
            previous_token = token

        updated_text = ' '.join(updated_tokens_tri)
        new_file_name = "/data/annual_reports_tess_ngrammed/" + filename[31:-4] + "_ngrammed.txt"
        with open(new_file_name, "w", encoding="utf-8") as outf:
            outf.write(updated_text)

#Efficient writing of the files
writepool = Pool(processors)
writepool.map(filewriter, text_files)
writepool.close()
writepool.join()
