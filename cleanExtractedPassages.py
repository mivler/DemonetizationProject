import random


infile = "risk_only_passages_uncleaned.tsv"
outfile = "risk_only_passages.tsv"
lines_in_file = 526548
sample_size = 100


def main():
    # Chooses random line numbers to sample
    line_lst = set([])
    while len(line_lst) < sample_size:
        line_num = random.randint(0, lines_in_file)
        line_lst.add(line_num)
    current_line = 0

    # Opens file in and file out
    with open(infile, "r", encoding="utf-8") as inf:
        with open(outfile, "w", encoding="utf-8") as outf:
            for line in inf:

                # gets file name without path, and gets passage text
                line_parts = line.split("\t")
                file_path_parts = line_parts[0].split("/")
                file_name = file_path_parts[len(file_path_parts) - 1]
                passage = line_parts[1]

                # Writes out both into out file if line is included in sample set
                text_line = file_name + "\t" + passage + "\n"
                if current_line in line_lst:
                    outf.write(text_line)
                current_line += 1


if __name__ == "__main__":
    main()
