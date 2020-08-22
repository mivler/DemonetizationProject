import glob
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD


# Matrix and SVD out files
matrix_outfile = "doc_words_matrix.npz"
svd_outfile = "svd_post_matrix.tsv"

# Infiles
path = "annual_reports_chunked/*.txt"
file_list = glob.glob(path)


def matrix_maker():
    """
    Creates a sparse matrix from the documents provided
    :return: tuple- (a sparse matrix representation of the corpus, vocab of matrix, features of matrix)
    """
    # Gets text from all documents
    doc_passages = []
    for file in file_list:
        with open(file, encoding="utf-8") as f:
            doc_passages.append(f.read())

    # Creates vectorizer, and limits features to get rid of misreadings
    vectorizer = TfidfVectorizer(max_features=100000)

    # Builds matrix
    matrix = vectorizer.fit_transform(doc_passages)

    # Get matrix vocab and features (ordered vocab)
    vocab = vectorizer.vocabulary_
    features = vectorizer.get_feature_names()

    # Save space
    del doc_passages
    return matrix, vocab, features


def save_matrix():
    """
    Saves the matrix made, and passes on the vocab and features
    :return: tuple- the vocab (unordered) and features (ordered like matrix) of the matrix
    """
    # Make matrix, extract important data
    matrix_info = matrix_maker()
    matrix = matrix_info[0]
    matrix_vocab = matrix_info[1]
    matrix_features = matrix_info[2]

    # Save matrix
    sparse.save_npz(matrix_outfile, matrix)
    return matrix_vocab, matrix_features


def embedding_of_words(matrix_file):
    """
    When passed a term to doc matrix file, takes the matrix, gets a set of term to component vectors
    :param matrix_file: str- an npz file containting a term document frequency sparse matrix
    :return: returns a truncated SVD with terms as vectors with 200 components for comparison
    """
    # Open matrix file
    matrix = sparse.load_npz(matrix_file)

    # Build truncator with limited components
    tsvd = TruncatedSVD(n_components=200)

    # make SVD model
    model = tsvd.fit_transform(matrix)
    return tsvd.components_


def main():
    """
    Creates a matrix, saves the vocab (unordered), and features (ordered) of that matrix
    Truncates matrix to get feature vectors for the corpus
    Write out feature matrix
    
    """
    # gets vocab and features
    vocab_features = save_matrix()
    vocab = vocab_features[0]
    features = vocab_features[1]

    # Writes out vocab
    with open("matrix_vocab.txt", "w", encoding="utf-8") as vocab_file:
        for k in vocab:
            vocab_file.write( k + "\n")

    # Writes out features
    with open("matrix_features.txt", "w", encoding="utf-8") as features_file:
        for k in features:
            features_file.write( k + "\n" )

    # Gets svd
    embedded_words = embedding_of_words(matrix_outfile)
    with open(svd_outfile, "w", encoding="utf-8") as outf:
       
        # Transpose for ideal orientation (1 feature per line)
        transposed = embedded_words.transpose()

        # Write out to file
        for elem in transposed:
            line = "\t".join([str(value) for value in elem])
            outf.write(line +"\n")


if __name__ == "__main__":
    main()
