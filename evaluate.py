"""
AriaRay Brown
June, 2022

[evaluate]
Test the accuracy of the phoneme-based n-gram model
using samples of IPA-text in known languages.
"""

from utilities import *
import text_to_ipa
import train_ngram
import identify
from tqdm import tqdm

SNIPPETS = "./test-docs/snippets.txt"

# For the future:
# TEST_DOCS = {}
# for l in LANGUAGES:
#     TEST_DOCS[l] = "./test-docs/"+l+".txt"


def _load_snippets(file):
    """
    Load snippets file. 
    Return dictionary of language keys, each with string sentence value.
    """
    snippets = {}

    with open(file, mode="r", encoding="utf-8") as f:
        f.readline() # skip headers

        for line in f:
            if not line.isspace():
                line = line.split("\t")
                lang = line[0]
                snippet = line[1]
                snippets[lang] = snippet
    return snippets


def test(sentence, lang, n_chars=None):
    """
    Test a string of known-language text using the 
    phoneme-based n-gram language identification model.

    param: sentence, string of text, treated as a sentence
    param: lang, string language abbreviation for the 
                 known language of the text
    param: n_chars, int number of chars of the given sentence
                    to identify. Defaults to full length of sentence.
    """
    if n_chars == -1: n_chars = len(sentence)
    sentence = sentence[:n_chars]

    phonemes = text_to_ipa.translate(sentence, lang)
    predictions = identify.identify_language(phonemes)
    language = identify.best(predictions)
    
    correct = (language == NAMED_LANGS[lang])

    return (predictions, lang, correct)


def test_snippets(file, n_chars=None, print_all=True):
    """
    Test accuracy of model on a single snippet of text from each trained language.

    param: file, path to tab-delimited txt file of snippets
    param: n_chars, int number of chars of the given sentence
                    to identify. Defaults to full length of sentence.
    return: results, a dictionary of top predicted languages with scores
                     for each language key.
    """
    snippets = _load_snippets(file)
    results = {}
    
    num_accurate = 0
    for lang in tqdm(snippets, desc="Testing snippets"):

        sentence = snippets[lang]
        result = test(sentence, lang, n_chars)
        
        results[lang] = result
        
        accurate = result[2]
        if accurate: num_accurate += 1
    
    accuracy = num_accurate/len(snippets)

    print("\nSnippets Identification Test\n")

    if print_all:
        for l, result in results.items():
            print(l + ": " + str(result) + "\n")
    else:
        for l, result in results.items():
            print(l + ": " + str(result[0][0][0]), result[1:])

    print("\nAccuracy:", str(num_accurate)+"/"+str(len(snippets)),"("+str(accuracy)+")")

    return results


def test_snippet_sizes(file):
    """
    Test accuracy of model on identifying the language
    of a single snippet of text in varying sizes from each trained language.

    param: file, path to tab-delimited txt file of snippets
    """
    print("\n****************************************")
    print("***Test Varying Snippet-of-Text Sizes***")
    print("****************************************\n")

    # Test varying sizes
    for n_chars in range(5,50,10):
        test_snippets(file, n_chars, print_all=False)
        print("--> when testing string length:", n_chars,"\n")

    # Test full length
    test_snippets(file, print_all=False)
    print("--> when testing full strings.\n")


# Run test functions as needed
if __name__ == "__main__":
    
    # text = "早晨，也稱為早上、晨、朝，字面上看就是辰时（日出后的时间）的前半段，早晨與日光及晚上合組成一天。但也有说法早晨为10点之前。"
    # result = test(text, "yue")
    # print("\n" + str(result))

    test_snippets(SNIPPETS)

    #use python3 evaluate.py >> results/snippet-sizes.txt in terminal
    test_snippet_sizes(SNIPPETS)



