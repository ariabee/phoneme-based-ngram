"""
AriaRay Brown
June, 2022

[train]
Train an ngram model on phoneme distributions in several languages.
"""

import math
import nltk
from nltk.lm import NgramCounter
from nltk import ngrams
from utilities import *
from tqdm import tqdm


# Dictionary of file paths for training corpora (documents in IPA for each language)
CORPORA = {}
for l in LANGUAGES:
    CORPORA[l] = "./ipa-documents/"+l+"-doc-in-ipa.txt"

END_UTTERANCE = "."
LANGUAGE_NGRAMS = {} # store here for access later


# Open and parse corpus files for phonemes
def load_corpus_phonemes(corpus_file, end_utterance_symbol = END_UTTERANCE):
    """
    Parse phonemes from corpus. 
    Return list of phonemes.

    param: corpus_file, string file path of corpus for parsing
    """

    phonemes = []
    with open(corpus_file, 'r', encoding='utf-8') as f:
        for line in f:
            chars = line.split()
            chars.append(end_utterance_symbol) # add a symbol to indicate the end of an utterance/sentence
            phonemes.extend(chars)
   
    return phonemes


# Create and store n-gram log probabilities for top k n-grams per language
def create_ngrams(tokens, n, k=0):
    """
    param: tokens, list of string tokens from which to compute n-grams
    param: n, int size of n-gram
    param: k, int size of most frequent n-grams to return (default is all n-grams)
    
    return: top_ngrams, a dict containing the top k ngrams as keys,
                        each with a dictionary containing keys ("count","log_prob")
                        for the raw counts of each ngram and the log probability of
                        the ngram given the number of all ngrams generated for the tokens.
    
                        Example: {"('ə', 'f', 'ə')" : {"count": 4, "log_prob": -3.09105},...}
    """

    # Generate list of ngrams with start and end padding
    grams = ngrams(tokens, n, left_pad_symbol="$", 
                              right_pad_symbol="/$", 
                              pad_left=True, 
                              pad_right=True)
    ngrams_list = list(grams)

    # Count ngrams
    ngram_counts = {}

    for ngram in ngrams_list:
        if ngram not in ngram_counts:
            ngram_counts[ngram] = 1
        else:
            ngram_counts[ngram] += 1

    # Total number of all ngrams
    sum_ngrams = sum(ngram_counts.values())

    # Sort ngrams based on frequency counts from highest to lowest
    ngram_counts = sorted(ngram_counts.items(), key = lambda x: x[1], reverse = True) # sorts the dict_items iterable based on the item values (x[1])

    # Set default k value to all unique ngrams
    if k == 0: k = len(ngram_counts) 

    # Trim list to top k ngrams
    ngram_counts = ngram_counts[:k]
    top_ngrams = {}
    for gram,count in ngram_counts:
        top_ngrams[gram] = {}
        top_ngrams[gram]["count"] = count # {('f', 'o', 'n'): {'count': 1} , ...} entries

    # Compute log probabilities for each ngram occurring in the corpus 
    # (these will be larger numbers, comparable to corpora of other sizes)
    for ngram in top_ngrams.keys(): # only compute log probs for the top ngrams
        prob = top_ngrams[ngram]["count"] / sum_ngrams
        log_prob = math.log(prob)
        top_ngrams[ngram]["log_prob"] = log_prob

    #print_grams(top_ngrams)

    return(top_ngrams)


def print_grams(top_ngrams, with_header=True):
    """
    Prettily print any ngrams from the create_ngrams output.
    """
   
    if with_header: print("\n\t\t\tcount\tlogprob")
    for gram in top_ngrams:
            print(str(gram) + ":\t" + str(top_ngrams[gram]["count"]) + ",\t" + str(top_ngrams[gram]["log_prob"]))


def print_l_grams(language_ngrams):
    """
    Prettily print the dictionary of language ngrams from training.

    param: language_ngrams, of the very particular form:
                            {"en": {"bigrams":[((("j","a"),3),-3.2345)], 
                                    "trigrams":...,
                                    "fourgrams":...},
                             "de": ..., ... }                 
    """
    for l in language_ngrams:
        for n in language_ngrams[l]:
            print("\n"+l+":\t\t\tcount\tlogprob")
            
            print_grams(language_ngrams[l][n], with_header=False)
    
    
# Compute dictionary of top k n-grams for each language
def train_languages(langs, k=0):
    """
    Creates a dictionary of n-grams for each language,
    that can be accessed in language identification. 

    param: langs, the list of languages to create ngrams for
    param: k, (optional) the int most frequent n-grams to find for each language
    returns: language_ngrams, a dictionary of dictionaries for 
                              each language, containing: 
                              bigrams, trigrams, four-grams.
    """
    language_ngrams = {}

    for l in langs:

        ngrams_dict = {}
        corpus = CORPORA[l]
        phonemes = load_corpus_phonemes(corpus)
        
        ngrams_dict["bigrams"] = create_ngrams(phonemes, 2, k)
        ngrams_dict["trigrams"] = create_ngrams(phonemes, 3, k)
        ngrams_dict["fourgrams"] = create_ngrams(phonemes, 4, k)

        language_ngrams[l] = ngrams_dict

    #print_l_grams(language_ngrams)
    return language_ngrams


# Run training functions as needed:
if __name__ == "__main__":

    #top_k = 100
    lang_grams = train_languages(LANGUAGES,5)
    print_l_grams(lang_grams)

    # Testing
    # phonemes = load_corpus_phonemes(CORPORA["de"])
    # top = create_ngrams(phonemes, 1)
    # print_grams(top)


