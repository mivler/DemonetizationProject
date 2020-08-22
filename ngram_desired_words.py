import regex
import csv
from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt
import nltk


# TSV file whose passages (the second portion of each line) are being ngrammed
input_file = "Loughran_Passages.tsv"

# Output file as tsv
outfile_name = "ngrammed_risk_passages.tsv"

# List bank
cash_words = ["cash", "cash_flow", "cash_reserves", "liquidity", "currency", "operating_cash_flow"]
borrowing_words = ["borrowing", "loan", "loans", "line_of_credit", "lines_of_credit", "credit", "trade_credit",
                   "bank", "banks", "creditors"]
demand_words = ["demand", "receives", "receivables", "demands", "customers", "transactions", "customer",
                "cash_payments"]
supply_words = ["supply", "suppliers", "supplier", "supply_chain", "payable", "payments", "payment", "cash_payments"]
capital_words = ["capital", "wages", "wage", "salaries", "salary", "working_capital", "raise_capital"]

# creation of all words list to ensure all words that need to be ngrammed are
all_lists = [cash_words, borrowing_words, demand_words, supply_words, capital_words]
all_words = []
for lst in all_lists:
    all_words.extend(lst)


def grammer_former(gram_size, upper_token_list):
    """
    creates a list of ngrammed tokens from a list of tokens
    :param gram_size: int- the size of the ngrams desired
    :param upper_token_list: list - list of tokens (not yet processed to be lowercase
    :return: list- a list of now ngrammed tokens
    """

    # Processing tokens, and prepping a set of previous words
    token_list = [token.lower() for token in upper_token_list]
    prior_words = token_list[0:(gram_size - 1)]

    # Adds first tokens to the updated_tokens
    updated_tokens = [token_list[i] for i in range(0, gram_size - 1)]

    # Goes through the rest of the tokens
    for token in token_list[gram_size:]:

        # creates ngram of prior words and new token
        prior_words.append(token)
        gram = "_".join(prior_words)

        # Adds ngrammed word to updated tokens and gets rid of the words that were in updated_tokens that are now in the ngram
        if gram in all_words:
            for i in range(0,gram_size-1):
                updated_tokens.pop()
            updated_tokens.append(gram)

        # Adds non-ngrammed token to updated_tokens
        else:
            updated_tokens.append(token)

        # gets rid of first word in prior words to keep prior words at desired length in a queue
        prior_words.pop(0)

    return updated_tokens


def process_line(line):
    """
    Takes in a line from the old tsv, and reformats it to have the filename, year, and ngrammed text
    :param line: str- the line of the tsv being processed
    :return: str- newly formatted/ngrammed line (see formatting difference above)
    """
    # Gets important attributes from line
    line_parts = line.split("\t")
    filename = line_parts[0].split("/")

    filename_split = filename[len(filename) - 1].split("_")
    year = int(filename_split[1][0:4])
    text = line_parts[1]

    # tokenizes passage
    tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)

    # Creates trigrammed and bigrammed tokens
    trigrammed_tokens = grammer_former(3, tokens)
    bigrammed_trigrammed_tokens = grammer_former(2, trigrammed_tokens)

    # puts together bigrammed and trigrammed text
    ngrammed_text = " ".join(bigrammed_trigrammed_tokens)

    # formats new line
    new_line = "{}\t{}\t{}\n".format(line_parts[0], year, ngrammed_text)

    return new_line


def main():
    # reading in file
    with open(input_file, "r", encoding="utf-8") as passages:
        line_list = [line for line in passages]

    # Runs efficiant execution of line processing
    processing_pool = Pool(30)
    new_lines = processing_pool.map(process_line, line_list)
    processing_pool.close()
    processing_pool.join()
    del line_list

    # writes out new passages and format (ngrammed and reformatted)
    with open(outfile_name, "w", encoding="utf-8") as outf:
        for line in new_lines:
            outf.write(line)


if __name__ == "__main__":
    main()
