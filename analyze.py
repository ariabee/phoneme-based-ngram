"""
AriaRay Brown
June, 2022

[analyze]
Analyze and inspect the frequency distribution of 
co-occurring phonemes (speech sounds) in multiple
languages.
"""

from utilities import *
import text_to_ipa
import train_ngram
import identify
import evaluate
import matplotlib.pyplot as plt
import nltk

LANGS = LANGUAGES[:-1] # don't include en_uk for analysis

lang_ngrams = train_ngram.train_languages(LANGS)

unigrams = []
bigrams = []
trigrams = []

# Inspecting shared unigrams, bigrams, and trigrams across languages
for l in lang_ngrams:
    # for gram in lang_ngrams[l]["unigrams"].keys():
    #     if lang_ngrams[l]["unigrams"][gram]["count"] > 2: # ensure that this phoneme occurs more than once
    #         bigrams.append(gram)
    for gram in lang_ngrams[l]["bigrams"].keys():
        if lang_ngrams[l]["bigrams"][gram]["count"] > 2:
            bigrams.append(gram)
    for gram in lang_ngrams[l]["trigrams"].keys():
        if lang_ngrams[l]["trigrams"][gram]["count"] > 2:
            trigrams.append(gram)

bigram_fd = nltk.FreqDist(bigrams) # shows most common based on number of languages that share the speech sound
print(bigram_fd.most_common(20)) 

trigram_fd = nltk.FreqDist(trigrams)
print(trigram_fd.most_common(20))

# unigram_fd = nltk.FreqDist(unigrams)
# print(unigram_fd.most_common(20)) 



# Show plots
#plt.show()

