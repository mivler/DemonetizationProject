"""
Authors: Matthew Ivler and Xanda Schofield
Takes a .doctopics.tsv output from a trained mallet model and takes the top num_top_docs number of documents that fall
under the different topics. Then it puts all the passages into a tsv formatted as topic number, filename, topic weight,
and file contents. This gives a sense of whether or not topics are appropriately conveying what we assume they convey 
based on the .keys.txt mallet output.
"""

import heapq

# Important variables at the top for easy changes
num_topics = 50
num_top_docs = 10
doctopics_filename = "AR_tesseract_4.doctopics.tsv"
output_filename = "best_docs_per_topic_4.tsv"


def main():
    # Initializes heap
    heap_list = []
    for i in range(num_topics):
        heap_list.append([])

    # Opens doc to read in
    with open(doctopics_filename, "r", encoding="utf-8") as doctop:

        # Takes first 10 docs and puts them in heap
        for i in range(num_top_docs):

            # Gets the separate pars of first 10 lines
            chunks = doctop.readline().split()
            line_filename = chunks[1]
            negative_topic_vals = [float(x) for x in chunks[2:]]

            # For each topic, goes in and fills adds the file to the heap
            for topic, neg_val in enumerate(negative_topic_vals):
                heapq.heappush(heap_list[topic], (neg_val, line_filename))

        # Should print out the number num_top_docs num_topics times to ensure all heaps are the same length
        for i in range(num_topics):
            print(len(heap_list[i]))

        # Repeats the above process, adding higher proportion documents and removing lower proportion ones
        # Retains size of num_top_docs for each heap
        for line in doctop:
            chunks = line.split()
            line_filename = chunks[1]
            negative_topic_vals = [float(x) for x in chunks[2:]]
            for topic, neg_val in enumerate(negative_topic_vals):
                heapq.heappushpop(heap_list[topic], (neg_val, line_filename))

    # Writes out the lines as:
    # topic number, file_name, proportion of doc (from doctopics file), and the passage from the file
    with open(output_filename, "w", encoding="utf-8") as outfile:
        for i in range(num_topics):
            # Check to make sure still at 10 docs per topic
            print(str(i) + " " + str(len(heap_list[i])))

            # Actual writing
            for neg_value, filename in heap_list[i]:
                filename_cut = filename[5:]
                with open(filename_cut, "r", encoding="utf-8") as infile:
                    passage = " ".join(infile.read().split())
                    out_line = "{0}\t{1}\t{2}\t{3}\n".format(i, filename_cut, neg_value, passage)
                    outfile.write(out_line)


if __name__ == "__main__":
    main()
