"""
Author: Matthew Ivler
Graphs the ratio of the numbers of uses of words from a given lexicon to the total number of words used in a certain
year based on the BSE annual reports corpus.
"""
import glob
import regex
import csv
from multiprocessing import Pool
import sys
import numpy as np
import matplotlib.pyplot as plt
import nltk


# Creates lexicon set from lowercased file with lexicon in it
lexicon_file_name = "/data/lexicon/Loughran_lower_lexicon.txt"
with open(lexicon_file_name) as lex:
    lexicon = set((line.strip() for line in lex))


# Creates set of files to count words from
path = "/data/annual_reports_tesseract/*.txt"
text_files = glob.glob(path)


def unigrams(filename):
    """
    Gets the counts of lexicon words for a given year from a single file
    :param filename: str- The name (inclusive of path) of the file being counted
    :return: tuple- (int- year, int- total number of words in file, int- total number of lexicon words in file)
    """
    # Get year from file name
    filename_split = filename.split("_")
    print(filename_split)
    year = int(filename_split[3][0:4])

    # Initialize count
    desired_word_count = 0

    with open(filename, encoding="utf-8") as f:
        # Read in and tokenizes text
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
        
        # Since each word should be a token, the total words will be the total tokens
        tot_words = len(tokens)

        # Creates a dictionary of lowercase words to their counts in the token list
        freq_dist = nltk.FreqDist([token.lower() for token in tokens])

        # Gets the total amount of lexicon words that were in the file based on frequency distribution counts
        for elem in lexicon:
            desired_word_count += freq_dist[elem]

        # Memory Cleanup
        del freq_dist
    return year, int(tot_words), int(desired_word_count)


def full_counts():
    """
    Creates dictionaries with years as keys where each year has the corresponding number of total words or lexicon
    words (dependent on dictionary)
    :return: tuple- (dict- year-to-lexiconWordCount, dict- year-to-TotalWordCount)
    """
    # Initialize the year-to-count dictionary for the total words and desired words
    tot_words_per_year = {}
    desired_words_per_year = {}
    for year in range(2010, 2020):
        tot_words_per_year[year] = 0
        desired_words_per_year[year] = 0

    # Multiprocessing used to make counting in files more efficient
    count_pool = Pool(35)
    counts_list = count_pool.map(unigrams, text_files)
    count_pool.close()
    count_pool.join()

    # Ensures proper formatting of list as well as a good progress check
    print(counts_list)

    # adds up counts to proper years in year-to-count dictionaries
    for (y, t, d) in counts_list:
        if y != 2009:
            tot_words_per_year[y] += t
            desired_words_per_year[y] += d
    return desired_words_per_year, tot_words_per_year


def graph_full_counts():
    """
    Graphs the ratio of lexicon words to total words for the annual reports of a given year.
    """

    # Gets dictionaries of 
    dicts = full_counts()
    desired_words_per_year = dicts[0]
    tot_words_per_year = dicts[1]
    
    # Set up x axis
    xs = [int(x) for x in range(2010, 2020)]
    # For cross checking later
    print(desired_words_per_year)
    print(tot_words_per_year)

    # Sorted lists based on counts from the dicts, sorted by year to correspond to the x-axis 
    desired = np.asarray([x[1] for x in sorted(desired_words_per_year.items(), key=lambda t: t[0])])
    total = np.asarray([x[1] for x in sorted(tot_words_per_year.items(), key=lambda t: t[0])])

    # Cross-check with pre-sorted prints to ensure sorting was correct
    print(desired)
    print(total)

    # Creats list of ratios
    ratio_desired_total = list(desired/total)

    # Conversion of y-axis to percentage
    ys = [y*100 for y in ratio_desired_total]

    # Plotting, labeling, saving
    plt.figure()
    plt.plot(xs, ys)

    plt.title("Ratio of Uncertainty Words to Total words by year (Laughran Lexicon)")
    plt.xlabel("Year")
    plt.ylabel("Uncertainty Words to Total Words (%)")

    out_file_name = "Uncertainty_Count_Ratio_Graph.png"
    plt.savefig(out_file_name)


def main():
    graph_full_counts()


if __name__ == "__main__":
    main()
