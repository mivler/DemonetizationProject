"""
Author: Matthew Ivler
Takes a file of ngrams and their counts, then puts them in order for easier diagnosis on what a good count cutoff is.
"""
filename = "trigrams_count.txt"
fileout = "trigrams_count_ordered.txt"
threshold = 100


def main():
    # Initialize dictionary {key = word : value = count}
    unordered_dict = {}
    
    # Creates ordered version of dictionary based
    with open(filename, "r", encoding="utf-8") as inf:
        for line in inf:
            line_split = line.split()
            unordered_dict[line_split[0]] = line_split[1]
    ordered_dict = {k:v for k, v in sorted(unordered_dict.items(), key=lambda x: int(x[1]))}
    
    # Writes ordered dictionary to outfile
    with open(fileout, "w", encoding="utf-8") as outf:
        for word, count in ordered_dict.items():
            line = word + " " + count + "\n"
            outf.write(line)


if __name__ == "__main__":
    main()
