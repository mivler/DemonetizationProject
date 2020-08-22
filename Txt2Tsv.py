"""
Author: Matthew Ivler
Converts a txt file to a tsv file because the doctopics is easier to view as a tsv.
"""
import sys

def main():
    """
    sys.argv[1]- str- argument for infile name (txt file to be converted)
    """
    file = sys.argv[1]
    o_file = "AR_tesseract_4.doctopics.tsv"
    with open(file, "r", encoding="utf-8") as inf:
        with open(o_file, "w", encoding="utf-8") as outf:
            for line in inf:
                line_split = line.split()
                new_line = "\t".join(line_split)
                newer_line = new_line + "\n"
                outf.write(newer_line)

if __name__ == "__main__":
    main()
