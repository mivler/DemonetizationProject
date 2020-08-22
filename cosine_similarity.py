import math
import heapq

# Sets up outfile with metadata
outfile = "similar_vectors.tsv"
# Sets up easily readable outfile
outfile_words = "similar_vectors_words.txt"
# Gets file of features (1 feature per line)
features_infile = "matrix_features.txt"
# svd matrix (1 feature per line)
svd_infile = "svd_post_matrix.tsv"
# words to compare to others
desired_features_list = ["uncertainty", "risk", "demonetization", "demonetize"]
# Number of desired vectors close desired words (num + 1 becuase of self)
num_top_vectors = 101
# Number of vector components used for comparison (must be less than components in matrix)
num_components = 101


def dot_product(x, y):
    """
    Calculates the dot product of two vectors
    :param x: list- list of floats (vector representing a term)
    :param y: list- list of floats (other vector representing a term)
    :return: float- the dot product of the two vectors
    """
    sum_num = 0
    for i in range(0, len(x)):
        sum_num += (float(x[i]) * float(y[i]))
    return sum_num


def magnitude(vector):
    """
    Calculates the magnitude of a vector
    :param vector: list- list of floats (vector representing a term)
    :return: float- the magnitude of the vector
    """
    sum_num = 0
    for i in range(0, len(vector)):
        sum_num += float(vector[i])**2
    return math.sqrt(sum_num)


def cosine_similarity(x, y):
    """
    Calculates the cosine similarity between two vectors
    :param x: list- list of floats (vector representing a term)
    :param y: list- list of floats (other vector representing a term)
    :return: float- a number between 0 and 1 representing similarity between two vectors (0 not close, 1 very close)
    """

    # Prints to ensure vectors are proper length
    print("x:", len(x))
    print("y:", len(y))

    # Calculates parts of cosine similarity
    numerator = dot_product(x, y)
    denominator = magnitude(x) * magnitude(y)

    # Avoids divide by 0 error
    if denominator == 0:
        return 0

    # returns cosine similarity
    else:
        cos_sim = numerator/denominator
        return cos_sim


def top_vectors(vector, svd_file):
    """
    Gets the num_top_vectors vectors that are most similar to the desired vectors
    :param vector: list- list of floats representing desired vector to get similar vectors for
    :param svd_file: str- name of file with truncated svd
    :return: heap- max heap of tuples sorted by cosine similarity with tuple values holding feature line number and feature vector
    """
    # Keeps track of line number
    line_number = 0

    # Gets important components from vector
    # Leaves out first component (since it's often related to frequency)
    vector = vector[1:num_components]

    # Initialize heap
    top_vecs_heap = []

    # Open file
    with open(svd_file, "r", encoding="utf-8") as svd:

        # Sets up first num_top_vectors features
        for i in range(0, num_top_vectors):
            line = svd.readline()

            # Update line number
            line_number += 1

            # Get's second vector
            vector_two = line.split("\t")
            vector_two = vector_two[1:num_components]

            # Get's cosine similarity
            sim = cosine_similarity(vector, vector_two)

            # Adds important info to heap
            heapq.heappush(top_vecs_heap, (sim, (line_number, vector_two)))

        # Continues past first num_top_vectors lines
        for line in svd:
            line_number += 1
            vector_two = line.split("\t")

            # Skips first component because it could be simply frequency related, and looks at first 100
            vector_two = vector_two[1:num_components]
            sim = cosine_similarity(vector, vector_two)
            heapq.heappushpop(top_vecs_heap, (sim, (line_number, vector_two)))

    return top_vecs_heap


def get_vector(features_file, svd_file, desired_feature):
    """
    Gets a vector given a desired feature
    :param features_file: str- file containing ordered features
    :param svd_file: str- file containing svd
    :param desired_feature: str- the word that we want the vector for
    :return: returns the vector that represents the desired feature
    """
    line_num = 0

    # Get's line of feature from feature file
    with open(features_file, "r", encoding="utf-8") as features:
        for line in features:
            line_num += 1
            word = line.strip()
            if word == desired_feature:
                break

    # Get's vector from svd_file on particular line (based on desired feature's line)
    vector_line = get_string_on_line(line_num, svd_file)

    vector = vector_line.split("\t")

    return vector


def get_string_on_line(line_num, file_name):
    """
    Get's the string on a particular line
    :param line_num: int- the desired line number
    :param file_name: str- the file we want the desired line from
    :return: str- the information on the line we desire (either a vector or a feature)
    """
    with open(file_name, "r", encoding="utf-8") as f:
        for i in range(0, line_num):
            line = f.readline()

    return line


def main():
    # initializes a dictionary of {key = desired_feature : value = vector of that feature}
    vector_dict = {}

    # Sets up dictionary of {feature : vector}
    for feature in desired_features_list:
        vector_dict[feature] = get_vector(features_infile, svd_infile, feature)

    with open(outfile, "w", encoding="utf-8") as outf:
        with open(outfile_words, "w", encoding="utf-8") as outfw:

            # Looks at the vectors of the desired features and gets the 100 most closely related feature
            # Based on cosine similarity of each features vector
            for feature, vector in vector_dict.items():
    
                # Gets top 100 similar vectors as a max-heap
                # (key = cosine similiary, value = (line of similar feature, vector of similar feature)
                top_vecs = top_vectors(vector, svd_infile)
    
                # Creates list of tuples 
                tuple_list = []

                # Fills in tuple list with tuples as (word with close vector, line of word and vector, cosine similarity measure)
                for elem in top_vecs:
                    sim = elem[0]
                    feature_line = elem[1][0]
                    word_represented = get_string_on_line(feature_line, features_infile)
                    tup = (word_represented.strip(), int(feature_line), float(sim))
                    tuple_list.append(tup)

                # tab separated (word/line/similarity) tuples
                info = "\t".join(["/".join([str(x) for x in tupe]) for tupe in sorted(tuple_list, key=lambda x:x[2], reverse=True)])
                # Writes out to file
                line_out = "{}\t{}\n".format(feature, info)
                outf.write(line_out)

                # space separated words in descending order based on similarity to desired word
                info = " ".join([str(tupe[0]) for tupe in sorted(tuple_list, key=lambda x: x[2], reverse=True)])
                line_out = "{}\t{}\n".format(feature, info)
                outfw.write(line_out)


if __name__ == "__main__":
    main()

