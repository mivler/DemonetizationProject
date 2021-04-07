from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from nltk import trigrams
import nltk
import glob
from functools import partial
import time
from multiprocessing import Pool
import pickle
import sys
import numpy as np
import string


# Set output files, directory of passages, and minimum document length
output_file = "perplexities_2017.tsv"
errors = "perplexity_errors.tsv"
direct = "/home/CAMPUS/mnia2018/annual_reports_chunked/"
min_doc_length = 20

# In case of random stop, starts from this year and this doc
start_year = 0
end_year = 0
start_doc = 0


def wordpunct_tokenize_no_nums_punct(sentence):
    tokens = wordpunct_tokenize(sentence)
    tokens_fixed = []
    for token in tokens:
        if token.isdigit():
            tokens_fixed.append("NUMBERITEM")
        elif token in string.punctuation:
            tokens_fixed.append("PUNCTITEM")
        else:
            tokens_fixed.append(token)
    return tokens_fixed


def get_perplex(file, model, error_file, timer):
    """
    Gets the perplexity of a given passage using a given language model based.
    :param file: str - The name of file containing a text passage
    :param model: lm object - a language model object from the nltk package
    :param error_file: str - the name of a file containing the file names and error types of files w/o perplexity
    :return: tuple - the file name and its corresponding perplexity score. Score is -1 if file is too short or -2
             if file encountered an error in calculation 
    """
    start = time.perf_counter()
    
    # Read file and tokenize
    with open(file, "r", encoding="utf-8") as infile:
        text = infile.read()
    tokens = wordpunct_tokenize_no_nums_punct(text)
    grams = [tuple(tokens)]

    # Checks for recursion error
    try:
        # Checks for appropriate file length and gets perplexity if long enough
        if len(tokens) >= min_doc_length:
            perplex = model.perplexity(grams)
        else:
            perplex = -1
    except:
        e = sys.exc_info()[0]
        with open(error_file, "a", encoding="utf-8") as err:
            print(str(e))
            err.write("\t".join([str(file), str(e)]) + "\n")
        perplex = -2

    end = time.perf_counter()


    del grams
    del tokens
    del end
    del start

    return perplex


def load_model(file_name):
    # Loads a language model from a .pkl file
    with open(file_name, "rb") as lm_f:
        lm_model = pickle.load(lm_f)
        print(sys.getsizeof(lm_model))
    return lm_model


def year_to_perplex(year):
    # Times process
    start = time.perf_counter()
    # Gets files, prints number of files in that year, loads model for that year
    files = glob.glob(direct + "*" + str(year+1) + "*.txt")
    print("Num files:", year, len(files))
    lm_file = "surpriseModel" + str(year) + ".pkl"
    lm = load_model(lm_file)

    with open(output_file, "a", encoding="utf-8") as out:
        if year == start_year:
            start_index = start_doc
        else:
            start_index = 0

        # Goes through files and writes out output
        for i in range(start_index, len(files)):
            # Gives a time every 500 docs to make sure perplexities aren't taking too long            
            if i%500 == 0:
                timer = True
            else:
                timer = False

            # Prints exact doc number in case it stops abruptly
            print("Current doc ", i, " for year ", year)

            # Writes out to file the (file name, year, perplexity) in tsv
            out.write("\t".join([files[i], str(year), str(get_perplex(files[i], lm, errors, timer))]) + "\n")


if __name__ == "__main__":
    # File resets, comment out if not starting process
    """
    with open(output_file, "w", encoding="utf-8") as out:
        print("reset outfile")
    with open(errors, "w", encoding="utf-8") as error_restart:
        print("reset error file")
    """
    # Start at current year and get perplexities
    for current_year in range(start_year, end_year):
        year_to_perplex(current_year)

