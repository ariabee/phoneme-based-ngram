"""
Computational Linguistics
Winter 2021/2022
AriaRay Brown
June, 2022

Final Project: Phoneme-Based Language Identification and Analysis Using N-Grams
"""

import utilities
import text_to_ipa
import train_ngram
import identify
import evaluate

# Step 1: Pre-process token-to-IPA dictionaries. (Processed files provided.)

# Step 2: Process training documents into IPA. (Processed files provided.)
# * Also provides utilites for translating any text into IPA,
#   and importantly, translating testing documents into IPA.

print("\ntext_to_ipa.translate('綠色城市。', 'yue')")
print("In IPA:", text_to_ipa.translate('綠色城市。', 'yue'))
print('\ntext_to_ipa.translate("good morning to all", "en")')
print("In IPA:", text_to_ipa.translate("good morning to all", "en"))

# Step 3: Train ngram models for each language.

language_ngrams = train_ngram.train_languages(utilities.LANGUAGES, k=20)
train_ngram.print_l_grams(language_ngrams)

# Step 4: Identify language from phonemes in IPA characters.
# * See examples in identify.py

# Step 5: Evaluate the phoneme-based n-gram language model using test documents.

evaluate.test_snippets(evaluate.SNIPPETS)

