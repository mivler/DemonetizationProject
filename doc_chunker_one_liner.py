import os
import sys
from multiprocessing import Pool

output_path = "annual_reports_chunked"
num_words = 300

def chunker(root_file):
    """
    Creates a chunked version of a text file where the new file is composed of several parts, each part being
    approximately num_words words long
    :param root: str- root of the in file
    :param file_name: str- name of file being chunked
    :param num_words: int- number of words per chunk
    :param output_path: str- path for chunked file directory
    :return: None
    """
    root = root_file[0]
    file_name = root_file[1]

    # Opens file to be read
    with open(root + "/" + file_name, "r", encoding="utf8") as file_in:
        # Sets text and initializes variables to be updated
        line = file_in.read().split()
        text_to_write = []
        section_num = 1
        word_count = 0
        for elem in line:
            word_count += 1
            text_to_write.append(elem)
            if word_count >= num_words:
                outfile_name = output_path + "/" + file_name[:-4] + "_" +  str(section_num) + "_out.txt"
                with open(outfile_name, "w", encoding="utf-8") as file_out:
                    file_out.write(" ".join(text_to_write))
                word_count = 0
                text_to_write = []
                section_num += 1
                
        if len(text_to_write) > 0:
            outfile_name = output_path + "/" + file_name[:-4] + "_" + str(section_num) + "_out.txt"
            with open(outfile_name, "w", encoding="utf-8") as file_out:
                file_out.write(" ".join(text_to_write))


def main():
    # sys.argv[1] (str) path to directory with text files
    
    path = sys.argv[1]
    root_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            tupe = (root, file)
            root_files.append(tupe)
    pool = Pool(35)
    pool.map(chunker, root_files)
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()

