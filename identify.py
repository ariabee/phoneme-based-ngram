"""
AriaRay Brown
June, 2022

[identify]
Identify the language of a string of IPA characters using ngrams.
"""

from utilities import *
import text_to_ipa
import train_ngram
from train_ngram import print_grams
import math

# Dictionary of ngrams stored for each language:
# {"en": {"bigrams": {(,): {"count": int, "log_prob": float} , ...}, 
#         "trigrams": ..., },
#         "fourgrams": ... }
#        }, ...
LANGUAGE_NGRAMS = train_ngram.train_languages(LANGUAGES)


def compute_ngrams(phonemes):
    """
    param: phonemes, the list of string phonemes 
    return: computed; a dictionary of lists of bigrams, trigrams, and four-grams
                      for the given phonemes
    """
    computed = {"bigrams":[],"trigrams":[],"fourgrams":[]}

    bigrams = train_ngram.create_ngrams(phonemes, 2)
    trigrams = train_ngram.create_ngrams(phonemes, 3)
    fourgrams = train_ngram.create_ngrams(phonemes, 4)

    computed["bigrams"] = bigrams
    computed["trigrams"] = trigrams
    computed["fourgrams"] = fourgrams

    # for n in computed:
    #     print("\n"+n+":\t\t\tcount\tlogprob")
    #     print_grams(computed[n], with_header=False)
    # print("\n")
    
    return computed


def score_similarity(text_ngrams):
    """
    Compare n-grams to each possible language profile to predict the language.
    Returns a list of tuples of similarity scores for each compared language.
    
    example return: [...,("french", 123),...]

    return: scores, a list of tuples in the form ((string language, float score),...)
    """
    scores = []

    for l in LANGUAGES:
        score = compare_language(text_ngrams, l)
        scores.append( (NAMED_LANGS[l], score) )

    # Sort scores highest to lowest
    scores = sorted(scores, key=lambda x:x[1], reverse=True)

    #print("scores: ", scores)
    return scores


def compare_language(ngrams_list, language, method="freq"):
    """
    Compares the given list of ngrams to the language profile 
    (frequency distribution of ngrams) in the given language.
    Returns a score for matching similarity.

    return: total_score, the float similarity score

    """
    total_score = 0
    lowest_prob = 0.0001128 # by taking lowest probability unigram across all languages, minus trailing digits
    
    if method=="freq":
    
        lang_profile = LANGUAGE_NGRAMS[language]

        w2 = 0.3 # weight of bigrams
        w3 = 0.6 # weight of trigrams
        w4 = 0.1 # weight of fourgrams

        weights = {"bigrams":w2,"trigrams":w3,"fourgrams":w4}

        # Compute weighted score for each size ngram
        for n in ngrams_list.keys():
            n_score = 0

            # Compute score for each ngram in test list
            for gram in ngrams_list[n]: 
                score = 0
                num_occur = ngrams_list[n][gram]["count"]
                
                # Check if test ngram exists in language ngrams
                if gram in lang_profile[n]:
                    score += lang_profile[n][gram]["log_prob"]
                
                # Else, using a smoothing method for unknown ngrams
                else:
                    # Current method: add a very low probability
                    score += math.log(lowest_prob)

                #print(gram, score)
            
                # Add log probabilities
                n_score += score + num_occur # weight by counts of ngram in string
            
            # Integrate total score with weighted scores for each n TODO: consider equation
            total_score += n_score - math.log(weights[n]) # since n_score is a log-prob, subtract weights to reduce probability
        
    return total_score


def identify_language(ipa):
    """
    Identify the language of a string of IPA characters
    by comparing its n-gram clusters of phonemes (speech sounds) 
    to the n-gram frequency distributions of possible languages.

    param: ipa, the string utterance in unicode IPA characters
    return: predicted_language, the string predicted language
    """
    
    # Parse ipa into phonemes
    phonemes = text_to_ipa.parse_ipa_input(ipa)

    # Compute n-grams for the transcribed phonemes
    text_ngrams = compute_ngrams(phonemes)

    # Compare n-grams to each possible language profile
    # to predict the language
    predictions = score_similarity(text_ngrams)

    return predictions


def best(predictions):
    """
    Returns highest-scoring language from identify_language(ipa).
    """

    predicted_language, score = max( predictions, key=lambda x:x[1] )
    return predicted_language

    # if type(predictions)==str:
    #     # Assume ipa
    #     ipa = predictions
    #     predicted_language, score = max( identify_language(ipa), key=lambda x:x[1] )
    #     return predicted_language


def identify(ipa):
    """
    Identify the language of a string of phonemes.
    Returns the (max-scoring) predicted language string.
    """
    predicted_language, score = max( identify_language(ipa), key=lambda x:x[1] )
    return predicted_language


"""
Test as needed:
"""
if __name__ == "__main__":
    
    lang_scores = identify_language("wʌt ə ˈbjutəfəl ˈmɔrnɪŋ")
    print("\nScores:" + str(lang_scores))
    
    lang = identify("wʌt ə ˈbjutəfəl ˈmɔrnɪŋ")
    print("\nLanguage identified:", lang, "\n")

    lang_scores = identify_language("j ɐ m h ɔː j ɐ n m ̩ h o u k aː j iː h ʊ k j ɪ ŋ w aː k j iː j iː k ɛː m ̩")
    print("\nScores:" + str(lang_scores), "\n")





