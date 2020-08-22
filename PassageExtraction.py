"""
Authors: Matthew Ivler and Xanda Schofield
Store passages as:
original file of passage, passage text, list of Loughran words in passage, number of Loughran words (TSV)

Passage contains no new line characters or tabs
If 2 Loughran words show up in the range, merge 2 passages (do not repeat overlap)
Words keep their internal punctuation when being checked against lexicon words.
Word spread set to 20 in the main
"""

import codecs
import os
import sys
import string

num_surrounding_words = 30


def prior_update(running_list, new_word):
    """
    Modifies running word list to be up to date on latest 20 words
    :param running_list: list - list of running words
    :param new_word: string - new word added to running list
    :return: Modified running list
    """
    running_list.pop(0)
    running_list.append(new_word)
    return running_list


def word_process(word):
    """
    format word (lowercase it get rid of ascii spec chars) so it can be compared to lexicon words
    :param word: str - a word
    :return: str - de-punctuated lowercase word
    """
    lowered = word.lower()
    return lowered.strip(string.punctuation).strip(string.whitespace)


def search_on(list_words, lexicon, current_word_index, word_spread):
    """
    Recursively build follow up passage after initial lexicon word sighting until there is a span of word_spread words
    that do not fall within the lexicon.
    :param list_words: list - all words in a doc (ordered)
    :param lexicon: set - set of all words in desired lexicon
    :param current_word_index: int - The spot in word list we are at (Note the current word is always a lexicon word)
    :param word_spread: int - the number of words we want around lexicon words
    :return: tuple - (Words that follow, words from the lexicon later in the passage, number of words later)
    """
    # Initialization
    follow_up_list = []
    lexicon_list = []
    words_after_current = word_spread

    # checks if near end of doc
    if (current_word_index + word_spread) < len(list_words):
        end = word_spread + 1
    else:
        end = len(list_words) - current_word_index
        words_after_current = end

    for i in range(1, end):

        # Check if lexicon word is met
        unprocessed_word = list_words[current_word_index + i]
        word = word_process(unprocessed_word)

        # Just add non-lexicon words
        if word not in lexicon:
            follow_up_list.append(unprocessed_word)

        else:
            follow_up_list.append(unprocessed_word)
            lexicon_list.append(word)
            recursed_tuple = search_on(list_words, lexicon, current_word_index + i, word_spread)
            follow_up_list.extend(recursed_tuple[0])
            lexicon_list.extend(recursed_tuple[1])
            words_after_current = i + recursed_tuple[2]
            break
    return tuple([follow_up_list, lexicon_list, words_after_current])


def write_out(infile_name, outfile_name, passage_list, lex_words):
    """
    Writes info out to file
    :param infile_name: str - name of infile
    :param outfile_name: str - name of outfile
    :param passage_list: list - list of strings to join into text passage
    :param lex_words: set - set of differing lexicon words that show up in passage
    :return: NONE
    """
    with open(outfile_name, "a", encoding="utf-8") as tsv:
        passage = ""
        for word in passage_list:
            processed_word = word.strip("\n\t")
            if passage == "":
                passage = processed_word
            else:
                passage = passage + " " + processed_word
        print(infile_name)
        print(codecs.encode(infile_name, encoding="utf-8"))
        print(type(passage))
        print("line: " + "{0}\t{1}\t{2}\t{3}\n".format(codecs.encode(infile_name, encoding="utf-8"), codecs.encode(passage, encoding="utf-8"), lex_words, len(lex_words)))
        tsv.write("{0}\t{1}\t{2}\t{3}\n".format(infile_name, passage, lex_words, len(lex_words)))


def file_parser(file_name, outfile_name, lexicon, word_spread):
    """
    Gets passages, number of Loughran words, list of Loughran words from lexicon
    :param file_name: str - path and name of file
    :param outfile_name: str - path and name of tsv to write to
    :param lexicon: set - set of words in the lexicon
    :param word_spread: int - number of words before and after lexicon word
    :return: NONE
    """
    # Open file, initialize word list
    list_words = []
    with open(file_name, "r", encoding="utf-8") as infile:
        # Create word list
        for line in infile:
            list_words.extend(line.split())

    current_word = 0
    passage_words = []
    # Look at each element, lowercase it, get rid of ascii spec chars (word check)
    # Track as first 20, check later 20, if nothing new in later 20, look at more
    while current_word < len(list_words):
        unprocessed_word = list_words[current_word]
        word = word_process(unprocessed_word)
        if word in lexicon:
            passage_words.append(unprocessed_word)
            text_tuple = search_on(list_words, lexicon, current_word, word_spread)
            passage_words.extend(text_tuple[0])
            lex_list = [word]
            lex_list.extend(text_tuple[1])
            current_word += text_tuple[2]

            # Checks following text to see if there would be overlap of lexicon words, and merges what would be
            # Two passages with slight overlap (ie 2 lexicon words 30 words away, but with a spread of 20 words would
            # have a 10 word overlap, so instead the passages are merged)
            follow_up_tuple = search_on(list_words, lexicon, current_word, word_spread)

            # If following words do require merging, then merge and keep checking until no lexicon words are found
            # in the potential overlap zone
            while len(follow_up_tuple[1]) != 0:
                # Builds up passage and lex list
                passage_words.extend(follow_up_tuple[0])
                lex_list.extend(follow_up_tuple[1])

                # Update current word index to rerun check
                current_word = current_word + follow_up_tuple[2]
                follow_up_tuple = search_on(list_words, lexicon, current_word, word_spread)
            # Appends new passage and details of passage to tsv
            write_out(file_name, outfile_name, passage_words, set(lex_list))

            # Prior words will always either be word_spread long (based on follow_up_tuple) or shorter (if end of doc)
            current_word = current_word + follow_up_tuple[2]
            passage_words = follow_up_tuple[0]

        # Accounts for start of doc, building up prior words list until it is word_spread long
        elif len(passage_words) < word_spread:
            passage_words.append(unprocessed_word)

        # just keep going about, and keeping track of last word_spread words
        else:
            passage_words = prior_update(passage_words, unprocessed_word)
        current_word += 1


def main():
    """
    arg(1) - lexicon file (txt format and each line is a new lexicon word)
    arg(2) - directory of files to process
    arg(3) - outfile (tsv)
    :return:
    """
    # Get's arguments
    lexicon_file_name = sys.argv[1]
    text_directory = sys.argv[2]
    outfile_name = sys.argv[3]

    # Creates lexicon set
    with open(lexicon_file_name) as lex:
        lexicon = set((line.strip() for line in lex))

    # Clears outfile
    with open(outfile_name, "w", encoding="utf-8") as tsv:
        pass

    # Loop over files, parses them, and writes them out to outfile one passage at a time
    for root, dirs, files in os.walk(text_directory):
        for file in files:
            file_name = root + "/" + file
            file_parser(file_name, outfile_name, lexicon, num_surrounding_words)


if __name__ == "__main__":
    main()
