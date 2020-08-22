import regex
import csv
from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt
import nltk
from collections import defaultdict


# Creates lexicon set
lexicon_file_name = "/data/lexicon/Loughran_lower_lexicon.txt"
with open(lexicon_file_name) as lex:
    lexicon = set((line.strip() for line in lex))

# list bank:
cash_words = ["cash", "cash_flow", "cash_reserves", "liquidity", "currency", "operating_cash_flow"]
borrowing_words = ["borrowing", "loan", "loans", "line_of_credit", "lines_of_credit", "credit", "trade_credit", "bank", "banks", "creditors"]
demand_words = ["demand", "receives", "receivables", "demands", "customers", "transactions", "customer", "cash_payments"]
supply_words = ["supply", "suppliers", "supplier", "supply_chain", "payable", "payments", "payment", "cash_payments"]
capital_words = ["capital", "wages", "wage", "salaries", "salary", "working_capital", "raise_capital"]
input_file = "ngrammed_risk_passages.tsv"
desired_list = cash_words
 

def list_processing(lst):
    """
    This function is obsolete with the addition of ngrams to the process
    """
    length_dict = defaultdict(lambda: [])
    for elem in lst:
        elem_split = elem.split()
        length_dict[len(elem_split)].append(elem)
    return length_dict


def passage_relation(line):
    """
    returns the year of a passage and whether or not it has one of the words from the desired list within it
    :param line: str- a line from the passages tsv
    :return: tuple(int, bool) year and true value if a desired word is in the passage
    """

    # Get's parts of the line
    line_parts = line.split("\t")

    # The year of the 
    year = int(line_parts[1][0:4])

    # Tokenizes text
    text = line_parts[2]
    tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)

    # If a desired word is in the passage, return true
    for elem in tokens:
        if elem.lower() in desired_list:
            return year, True

    return year, False


def passage_counts():
    """
    Creates two dictionaries. One of passages per year, and one of passages with words from the desired list per year
    :return: tuple- (dictionary of desired passages by year, dictionary of number of total passages by year)
    """

    # gets a list of all passage lines
    with open(input_file, "r", encoding="utf-8") as passages:
        line_list = [line for line in passages]

    # Initializes dictionaries
    tot_passages_per_year = {}
    desired_passages_per_year = {}

    # Sets up keys in both dictionaries
    for year in range(2010, 2020):
        tot_passages_per_year[year] = 0
        desired_passages_per_year[year] = 0

    # Multiprocessing for efficiency
    count_pool = Pool(30)
    counts_list = count_pool.map(passage_relation, line_list)
    count_pool.close()
    count_pool.join()

    # Save space 
    del line_list

    # Counts if a passage is related to the desired topic
    for y, related in counts_list:
        if y != 2009:
            tot_passages_per_year[y] += 1
            if related:
                desired_passages_per_year[y] += 1
    return desired_passages_per_year, tot_passages_per_year


def graph_passages():
    """
    graphs years on the x axis and the ratio of passages related to desired topic to total passages on the y-axis
    """

    # gets important dictionaries
    dicts = passage_counts()
    desired_words_per_year = dicts[0]
    tot_words_per_year = dicts[1]

    # Creats x-axis values
    xs = [int(x) for x in range(2010, 2020)]

    # Prints for progress and quality check
    print(desired_words_per_year)
    print(tot_words_per_year)

    # Sorting, and creation of two arrays to calculate y-axis. Prints to check to make sure sorting worked on right key
    desired = np.asarray([x[1] for x in sorted(desired_words_per_year.items(), key=lambda t: t[0])])
    print(desired)
    total = np.asarray([x[1] for x in sorted(tot_words_per_year.items(), key=lambda t: t[0])])
    print(total)

    # Create y-axis
    ratio_desired_total = list(desired/total)
    ys = [y*100 for y in ratio_desired_total]
    print(ratio_desired_total)

    # Plotting
    plt.figure()
    plt.plot(xs, ys)

    plt.title("Proportion of Risk Passages Associated With " + desired_list[0] + " (Laughran Lexicon)")
    plt.xlabel("Year")
    plt.ylabel("Proportion of Passages Associated With " + desired_list[0])

    out_file_name = desired_list[0] + "_relation_to_risk.png"
    plt.savefig(out_file_name)


def main():
    graph_passages()


if __name__ == "__main__":
    main()
