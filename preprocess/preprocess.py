from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import sklearn.decomposition
import numpy as np
import math
import glob
import os
import re
import json
import sys
from pathlib import Path
from symspell_rs import SymspellPy
import scipy
from multiprocessing import Pool
import fasttext
import fasttext.util
import time

# Parameters
collection = os.getenv("collection")
language = os.getenv("language", "en")
DATA_DIR = os.getenv("code_dir", "/code/data")

print("GOT PARAMS", {"collection": collection, "language": language})

text_dir = os.path.join(DATA_DIR, "collections", collection)
embedding_dir = os.path.join(DATA_DIR, "embeddings")
embedding_model = os.path.join(embedding_dir, f"cc.{language}.300.bin")
output_dir = os.path.join(DATA_DIR, "models", collection)
vocab_size = 30_000
token_pattern = re.compile("(?u)\\b\\w\\w+\\b")

# Create output/embedding directories if they don't exist
Path(output_dir).mkdir(parents=True, exist_ok=True)
Path(embedding_dir).mkdir(parents=True, exist_ok=True)

# Helper functions
def alpha_num_order(string):
    # Sort in natural order: https://stackoverflow.com/a/39885192
    return "".join(
        [
            format(int(x), "020d") if x.isdigit() else x
            for x in re.split(r"(\d+)", string)
        ]
    )


def read_fn(fn):
    # Read and return file contents
    with open(fn, "r") as f:
        return f.read()


start_time = time.monotonic()


def print_ts(msg):
    # Print with timestamp
    elapsed = time.monotonic() - start_time
    seconds = elapsed % 60
    minutes = math.floor(elapsed / 60)
    timestamp = f'[{"{0:02d}".format(minutes)}:{"{0:05.2f}".format(seconds)}]'
    print(timestamp, msg)


# Get all text files
print_ts("Reading all text files")
text_file_names = sorted(
    glob.glob(os.path.join(text_dir, "*.txt")), key=alpha_num_order
)
text_files = [read_fn(text_file) for text_file in text_file_names]
num_documents = len(text_files)
total_chars = int(np.sum([len(text_file) for text_file in text_files]))
total_words = int(
    np.sum([len(list(filter(bool, text_file.split(" ")))) for text_file in text_files])
)
avg_chars = total_chars / num_documents
avg_words = total_words / num_documents


# Derive counts for all words
print_ts(
    f"Deriving counts over corpus (N={num_documents}, avg words={'{:0.2f}'.format(avg_words)})"
)
count_vectorizer = CountVectorizer(strip_accents="unicode", stop_words=None)
counts = count_vectorizer.fit_transform(text_files)

# Calculate word frequencies
count_by_word = np.sum(counts, axis=0).getA().flatten()
features = count_vectorizer.get_feature_names()
num_uncompressed_features = len(features)
frequencies = np.flip(np.argsort(count_by_word))

# Reduce vocabulary to most frequent words
vocab = set([features[idx] for idx in frequencies[:vocab_size]])

# Create a small bigram model on most frequent words to filter down vocabulary quickly
print_ts("Creating bigram model")
bigram_char_vectorizer = TfidfVectorizer(ngram_range=(2, 2), analyzer="char_wb")
char_counts = np.asarray(
    bigram_char_vectorizer.fit_transform(
        [" ".join([features[idx] for idx in frequencies[:vocab_size]])]
    ).todense()
)[0]


def get_bigram_prob(word):
    # Approximate probability of bigram chars
    text = f" {word} "
    prob = 0
    count = 0
    for i in range(len(text) - 1):
        bigram = text[i : i + 2]
        prob += math.log(char_counts[bigram_char_vectorizer.vocabulary_.get(bigram, 0)])
        count += 1
    return prob / count


# Create spelling dictionary
dictionary_path = os.path.join(output_dir, "spelling_dictionary.txt")
with open(dictionary_path, "w") as f:
    for i in range(min(num_uncompressed_features, vocab_size)):
        idx = frequencies[i]
        word, freq = features[idx], count_by_word[idx]
        f.write(f"{word} {freq}\n")
    f.close()

# Load spelling dictionary into symspell
sym_spell = SymspellPy(2, 9)
sym_spell.load_dictionary(dictionary_path, 0, 1, " ")


def get_terms(word):
    # Return the same word if it's in the vocab
    if word in vocab:
        return [count_vectorizer.vocabulary_[word]]

    # Quick pass: remove overly long or improbable words
    if len(word) > 20 or get_bigram_prob(word) < -4:
        return []

    def get_terms_raw():
        # Use symspell's compound search to potentially split apart words
        spell_checked = sym_spell.lookup_compound(word, 2)[0].term.split(" ")
        return spell_checked

    terms = get_terms_raw()
    # Filter terms to only include those in the reduced vocab
    return [count_vectorizer.vocabulary_[x] for x in terms if x in vocab]


print_ts(f"Spell-reducing the vocabulary ({num_uncompressed_features} to {vocab_size})")
with Pool(12) as p:
    mappings = list(p.imap(get_terms, features, chunksize=500))

# with Pool() as p:
#     # With multiple threads spell-correct the extended vocabulary
#     mappings = list(p.imap(get_terms, features, chunksize=500))

# Re-compute the entire corpus with a spell-correcting tokenizer
def spell_correcting_tokenizer(s):
    tokens = token_pattern.findall(s)
    results = []
    for token in tokens:
        idx = count_vectorizer.vocabulary_[token]
        results += [features[i] for i in mappings[idx]]
    return results


# Derive tf-idf data on spell-corrected corpus
print_ts("Deriving tf-idf on spell-reduced corpus")
spell_corrected_vectorizer = TfidfVectorizer(
    strip_accents="unicode", stop_words=None, tokenizer=spell_correcting_tokenizer
)
spell_corrected_tfidf = spell_corrected_vectorizer.fit_transform(text_files)
spell_corrected_features = spell_corrected_vectorizer.get_feature_names()

# Serialize tf-idf data
scipy.sparse.save_npz(os.path.join(output_dir, "tfidf.npz"), spell_corrected_tfidf)

# Project tf-idf data down in dimensionality
print_ts("Applying SVD to lower dimensionality of TF-IDF")
svd_transformer = sklearn.decomposition.TruncatedSVD(
    300, algorithm="randomized", n_iter=5
)
doc_svd = svd_transformer.fit_transform(spell_corrected_tfidf)

# Calculate doc embeddings
print_ts("Loading embedding model")
# Download the embedding model if not present
working_dir = os.getcwd()
os.chdir(embedding_dir)
fasttext.util.download_model(language, if_exists="ignore")
os.chdir(working_dir)
model = fasttext.load_model(embedding_model)
embedding_vectors = np.array(
    [model.get_word_vector(feature) for feature in spell_corrected_features]
)
print_ts("Computing doc embeddings")
doc_embeddings = np.dot(spell_corrected_tfidf.A, embedding_vectors)

# Doc vectors are just doc_svd and doc_embeddings concatenated
doc_vectors = np.hstack((doc_svd, doc_embeddings))

# Serialize doc vectors to file
print_ts("Writing full doc vectors and settings")
np.savez_compressed(os.path.join(output_dir, "doc_vectors.npz"), doc_vectors)

# Write parameters
with open(os.path.join(output_dir, "params.json"), "w") as f:
    json.dump(
        {
            "text_dir": os.path.relpath(os.path.abspath(text_dir), output_dir),
            "num_documents": num_documents,
            "total_chars": total_chars,
            "avg_chars": avg_chars,
            "total_words": total_words,
            "avg_words": avg_words,
            "embedding_model": os.path.relpath(
                os.path.abspath(embedding_model), output_dir
            ),
            "vocab_size": vocab_size,
            "uncompressed_vocab_size": num_uncompressed_features,
            "token_pattern": token_pattern.pattern,
        },
        f,
        indent=4,
    )

print_ts("SUCCESS")
