from nltk.tokenize import wordpunct_tokenize, sent_tokenize
from nltk.lm import KneserNeyInterpolated
from nltk import trigrams
from nltk.lm.preprocessing import padded_everygram_pipeline
import nltk
import glob
import time
from multiprocessing import Pool
import pickle
from nltk.lm import Vocabulary
import string


vocab_file = "surprise_vocab.tsv"


def load_vocab(vocab):
    """
    loads the vocab (~50000 words) into a list
    """
    with open(vocab, "r", encoding="utf-8") as infile:
        vocab_list = [line.strip("\n") for line in infile]
    return vocab_list


def wordpunct_tokenize_no_nums_punct(sentence):
    """
    Replace number strings with "NUMBERITEM" (in vocab) and punctuation with "PUNCTITEM" (also added to vocab)
    """
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


def tokenized_docs(file_name):
    """
    Gets docs into a format of a list of a list of tokens, where internal token lists represent sentences
    and the outer list represents the document. 
    """

    with open(file_name, "r", encoding="utf-8") as in_file:
        text = in_file.read()

    sentences = sent_tokenize(text)
    tokens = [wordpunct_tokenize_no_nums_punct(sentence) for sentence in sentences]
    return tokens


def process_test(doc_name, test_sentence_in, test_sentence_some, test_sentence_not):
    """
    Old small test function
    """
    corpus_sentences = tokenized_docs(doc_name)
    lm = build_model(corpus_sentences)

    # Give test perplexities for a sentence in the corpus, with some parts from the corpus, and with no corpus relation
    print(lm.perplexity(trigrams(wordpunct_tokenize(test_sentence_in))))
    print(lm.perplexity(trigrams(wordpunct_tokenize(test_sentence_some))))
    print(lm.perplexity(trigrams(wordpunct_tokenize(test_sentence_not))))


def model_test():
    """
    Old small test function
    """
    start = time.perf_counter()
    test_in = "Pursuant to clause 31 of the Listing"
    test_some_in = "Perquisites shall be evaluated as per the goat cheese exemption, cowboy"
    test_not_in = "Howdy, doodle! Yankee Poodle! Somebody devoured Einstein's pewl noodle??"
    process_test("GGDANDE_2013.txt", test_in, test_some_in, test_not_in)
    end = time.perf_counter()
    print(end - start)


def merge_doc_sentences(doc_sentences):
    # Joining the lists within the doc_sentences to make a single list of all sentences in the corpus
    corpus_sentences = []
    for i in range(0, len(doc_sentences)):
        corpus_sentences.extend(doc_sentences.pop(0))
    return corpus_sentences


def build_model(corpus_sentences):
    """
    Builds the model
    :param corpus_sentences: a list of the tokenized sentences from the entire corpus
    :return:
    """
    vocab_list = load_vocab(vocab_file)

    # Create and fit model to text
    lm = KneserNeyInterpolated(3, vocabulary=Vocabulary(vocab_list))
    text, vocab = padded_everygram_pipeline(3, corpus_sentences)
    lm.fit(text, vocab)

    # Check for appropriate model size
    print("lm vocab size: ", len(lm.vocab))

    return lm


def model_make_and_save(year_desired):
    start = time.perf_counter()

    files_paths = "/data/annual_reports_tesseract/*" +str(year_desired) + "*.txt"
    files = glob.glob(files_paths)
    pool = Pool(30)
    lst_of_doc_tokens = pool.map(tokenized_docs, files)
    pool.close()
    pool.join()

    corpus_sentences = merge_doc_sentences(lst_of_doc_tokens)
    model = build_model(corpus_sentences)
    outfile_name = "surpriseModel" + str(year_desired) + ".pkl"
    with open(outfile_name, "wb") as model_file:
        pickle.dump(model, model_file, pickle.HIGHEST_PROTOCOL)
    end = time.perf_counter()
    elapsed = (end - start) / 60
    print("Time to run:", elapsed)
    return model


if __name__ == "__main__":
    nltk.download("punkt")
    
    years = range(2016, 2017)

    for year in years:
        model_make_and_save(year)
