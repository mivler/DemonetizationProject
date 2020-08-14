import os
import sys


def chunker(root, file_name, num_words, output_path):
    """
    Creates a chunked version of a text file where the new file is composed of several parts, each part being
    approximately num_words words long
    :param root: str- root of the in file
    :param file_name: str- name of file being chunked
    :param num_words: int- number of words per chunk
    :param output_path: str- path for chunked file directory
    :return: None
    """

    # Opens file to be read
    with open(root + "/" + file_name, "r", encoding="utf8") as file_in:
        # Sets text and initializes variables to be updated
        last_line = file_in.readline().split()
        text_to_write = []
        section_num = 0
        more_than_one_line = False
        outfile_name = output_path + "/" + file_name[:-4] + "_out.txt"
        file_out = open(outfile_name, "w", encoding="utf8")

        for line in file_in:
            more_than_one_line = True
            # Sets current line
            current_line = line.split()

            if (last_line == "\n"): 
                pass

	    # Writes what is before the two short lines
            elif (len(current_line) + len(last_line)) <= 10:
                text_to_write.extend(last_line)
                file_out.write("{0}_{1}\t{0}\t{2}\n".format(file_name[:-4], section_num, ' '.join(text_to_write)))
                text_to_write = []
                section_num += 1

            # For when current line and last line check out, adds last line
            # (Reasoning: current line may not check out with following line)
            else:
                text_to_write.extend(last_line)

            # Enough words, now write to file
            if len(text_to_write) >= num_words:
                # Resets initialized variables and updates which chunk it's on
                file_out.write("{0}_{1}\t{0}\t{2}\n".format(file_name[:-4], section_num, ' '.join(text_to_write)))
                text_to_write = []
                section_num += 1

            # Update last line for next loop run
            last_line = current_line

        # Writes the final part of the file to the file if the final part is not enough words long
        if more_than_one_line and len(text_to_write) > 0:
            text_to_write.extend(last_line)
            file_out.write("{0}_{1}\t{0}\t{2}\n".format(file_name[:-4], section_num, ' '.join(text_to_write)))

        # Handles case where file is considered as "one line" in length (not typically formatted files)
        else:
            word_count = 0
            for elem in last_line:
                word_count += 1
                text_to_write.append(elem)
                if word_count >= num_words:
                    file_out.write("{0}_{1}\t{0}\t{2}\n".format(file_name[:-4], section_num, ' '.join(text_to_write)))
                    word_count = 0
                    text_to_write = []
                    section_num += 1

        file_out.close()


def main():
    # sys.argv[1] (str) path to directory with text files
    # sys.argv[2] (int) number of words per chunk
    # sys.argv[3] (str) path to directory for files to end up in
    path = sys.argv[1]
    for root, dirs, files in os.walk(path):
        for file in files:
            chunker(root, file, int(sys.argv[2]), sys.argv[3])


if __name__ == "__main__":
    main()

