"""
Author: Matthew Ivler and Julien Luebbers
Graphs the proportion each topic over the years for a given corpus and a given Mallet doctopics output.
"""

import numpy as np
import matplotlib.pyplot as plt


# Easy access vaariables
doctopics_file = "/home/CAMPUS/mnia2018/AR_4/AR_tesseract_4.doctopics.txt"
num_topics = 50
topics_list = range(0, num_topics)


def get_dicts():
    """
    Get's the top_year_dicts and docs_in_year for graphing
    :return: tuple- (list of dictionaries {key = year : value = sum of topic proportions}, dict of docs per year {key = year : value = docs that year})
    """

    # Initializes a dictionary of {key = year : value = number of documents that year}
    num_docs_per_year = {}

    # Intializes a list of dictionaries whose indices represent the topic they represent
    # dictionaries are {key = year : value = sum of proportions of documents for given topic}
    proportion_list = []
    for i in range(num_topics):
        proportion_list.append({})

    with open(doctopics_file, "r", encoding="utf-8") as doctop:
        # Gets the year for each line in doctopics file, adding 1 to number of docs that year
        # And adding proportions of each topic for that year in proprotion_list
        for line in doctop:

            # Get year
            splt = line.split()
            file_name = splt[1].split("_")
            year = int(file_name[3][0:4])

            # Puts initial numbers in for each year not year present in the dictionaries
            if year not in num_docs_per_year.keys():
                num_docs_per_year[year] = 1
                for i in range(0, num_topics):
                    proportion_list[i][year] = 0

            # Does normal summing for years already in dictionary
            else:
                num_docs_per_year[year] += 1

            # Adds proprotions for each topic
            for i in range(0, num_topics):
                proportion_list[i][year] += float(splt[i+2])
    return proportion_list, num_docs_per_year


def topicOverTime(t, important_dicts):
    """
    Plots a given topic over the years
    :param t: integer, topic number from 1-50 (NOTE: this is different from df indexing.)
    :param important_dicts: tuple of dicts. - one for proportions of each topic each year, one for num docs each year
    """
    # Parses important dicts for each dict
    top_year_dicts = important_dicts[0]
    docs_per_year = important_dicts[1]

    # Plotting
    plt.figure()
    # Gets x axis
    xs = [int(x) for x in sorted(top_year_dicts[t].keys())][1:]
    
    # sorting by years to get proportions of each topic in order by year and counts of documents in order by year
    if docs_per_year:
        doc_props = [x[1] for x in sorted(top_year_dicts[t].items(), key=lambda y: y[0])][1:]
        doc_counts = [x[1] for x in sorted(docs_per_year.items(), key=lambda y: y[0])][1:]
    
    # Creates y-axis values 
        ys = list(np.asarray(doc_props)/np.asarray(doc_counts))
    else:
        ys = list(top_year_dicts[t].values())

    # Plotting, labeling, saving
    plt.plot(xs, ys)
    if docs_per_year:
        plt.title("Topic %i Over Time" %t)
    else:
        plt.title("Topic %i being a top Topic over Time" %t) # Kwarg: balance with total number of docs from each year
    plt.xlabel("Year")
    plt.ylabel("Topic %i Proportion Over Number of Documents By Year" %t)

    out_file_name = "topic_" + str(t) + "avg_proportion_by_year.png"
    plt.savefig(out_file_name)
    plt.close()


def main():
    important_dictionaries = get_dicts()
    for elem in topics_list:
        topicOverTime(elem, important_dictionaries)


if __name__ == "__main__":
    main()
