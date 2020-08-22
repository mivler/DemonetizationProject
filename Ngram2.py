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
    if gram[0] in stops or gram[1] in stops:
        return ""
    elif len(gram[0].split("_")) == 2:
        bigram_split = gram[0].split("_")
        if bigram_split[0] in stops:
            return ""
    else:
        return gram


def unigrams(filename):
    with open(filename, encoding="utf-8") as f:
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
    return nltk.FreqDist([token.lower() for token in tokens])


unipool = Pool(processors)
unigram_dists = unipool.map(unigrams, text_files)
for freqdist in unigram_dists:
    word_fd.update(freqdist)
unipool.close()
unipool.join()

# Only keeps the most frequent unigrams
word_fd_frequent = set([word for word, count in word_fd.items() if count >= freq_min])

del unigram_dists
del word_fd

bigram_fd = nltk.FreqDist()
print("Unigrams complete")


def bigrams(filename):
    with open(filename, encoding="utf-8") as f:
        text = f.read()
        tokens = regex.findall(r"\p{IsAlphabetic}(?:[[:punct:]]?\p{IsAlphabetic})*", text)
        bigrams = nltk.bigrams(token.lower() for token in tokens)
        bigrams_filtered = [bigram for bigram in bigrams if bigram[0] in word_fd_frequent and bigram[1] in word_fd_frequent]
    del bigrams
    bigrams_cleaned = [bigram for bigram in bigrams_filtered if element_clean(bigram) != ""]
    del bigrams_filtered
    return nltk.FreqDist(bigrams_cleaned)


bipool = Pool(processors)
bigram_dists = bipool.map(bigrams, text_files)
for freqdist in bigram_dists:
    bigram_fd.update(freqdist)
bipool.close()
bipool.join()

with open("bigrams_count.txt", "w", encoding="utf-8") as out:
    for word, count in bigram_fd.items():
        bigram = word[0] + "_" + word[1]
        line = bigram + " " + str(count) + "\n"
        out.write(line)

# Only keeps the frequent bigrams
bigram_fd_frequent = set([word for word, count in bigram_fd.items() if count >= freq_min])
del bigram_dists
del bigram_fd

del word_fd_frequent

print("bigram complete")

bigram_trigram_fd = nltk.FreqDist()


def trigrams(filename):
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
                # word_fd_frequent.add(token)
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


tripool = Pool(20)
trigram_dists = tripool.map(trigrams, text_files)
for freqdist in trigram_dists:
    bigram_trigram_fd.update(freqdist)
del trigram_dists
tripool.close()
tripool.join()
print("trigrams almost done")

with open("trigrams_count.txt", "w", encoding="utf-8") as out:
    for word, count in bigram_trigram_fd.items():
        trigram = word[0] + "_" + word[1]
        line = trigram + " " + str(count) + "\n"
        out.write(line)

bigram_trigram_fd_frequent = set([word for word, count in bigram_trigram_fd.items() if count >= freq_min])
del bigram_trigram_fd

print("trigrams complete\nwriting...")


def filewriter(filename):
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


writepool = Pool(processors)
writepool.map(filewriter, text_files)
writepool.close()
writepool.join()
