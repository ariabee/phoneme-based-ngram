"""
AriaRay Brown
June, 2022

[convert]
Convert documents from text to IPA (phonemes) for ngram training. 

Supports languages: 
[] English (North American) (en)
[] German (de)
[] Spanish (es)
[] French (fr)
[] Italian (it)
[] Korean (ko)
[] Polish (pl)
[] Russian (ru)
[] Turkish (tr)
[] Cantonese (yue)
"""

import csv
import utilities
from utilities import LANGUAGES, DIACRITICS, ACCENTS, DOCUMENT_PATH, IPA_PATH, NAMED_LANGS, DEBUG
import nltk
import jieba
jieba.setLogLevel(20) # hide initializing message
from nltk.stem import SnowballStemmer
import os
import re
from tqdm import tqdm

# Create directory for storing IPA-translated training documents
IPA_DOCS = "./ipa-documents/"
if not os.path.isdir(IPA_DOCS):
	os.mkdir(IPA_DOCS)

# Save unhandlded token information
unhandled_sents = {}
unhandled_tokens = {}
unhandled_tokens_list = {}
transcribed_tokens = {}
contains_word_cases = {}
for l in LANGUAGES:
    unhandled_tokens[l] = 0
    unhandled_tokens_list[l] = []
    transcribed_tokens[l] = 0
    unhandled_sents[l] = 0
    contains_word_cases[l] = 0

# Organize language files (ipa dictionary csv, document) in dictionary
# Store built IPA dictionary objects.
languages = {}
for l in LANGUAGES:
    languages[l] = {"ipa_csv": l+".csv", "doc_file": l+".txt", "ipa_dict": {}}
languages["en_uk"]["doc_file"] = "en.txt" # exception



# Get supported languages
def lookup_languages():
    """
    Returns a list of supported language abbreviations.
    """
    for l in NAMED_LANGS:
        print(l + ": " + NAMED_LANGS[l])

    return NAMED_LANGS

# Check language formatting
def check_languages():
    """
    Check formatting of tokens and transcriptions for each language.
    """
    #all_chars = ""
    for l in LANGUAGES:

        next_lang = input("\nCheck next language, " + l + "? [y/n] ")

        if (next_lang.lower()!="n"):
            
            # Check each language
            lang = languages[l]
            doc = DOCUMENT_PATH + lang["doc_file"]
            ipa = IPA_PATH + lang["ipa_csv"]

            # Open IPA dictionary csv
            with open(ipa, "r", encoding="utf-8", newline="") as ipa_csv:
                ipa_reader = csv.reader(ipa_csv)
                for line in ipa_reader:
                    entry = line
                    token = entry[0].lower()
                    # print(token)
                    transcription = entry[1:]
                    # print(transcription)

                    for form in transcription:
                        #print(form)
                        split_form = form.split()
                        for char in split_form:
                            # if char not in all_chars:
                            #     all_chars += char + " "
                            if len(char) > 1:
                                #print(char)
                                pass
                    # if (len(transcription) > 1):
                    #     print(transcription)

            print("\nComplete.\n")

        else:
            continue

# Clean IPA transcription
def clean_ipa(transcription):
    """
    Clean IPA transcription to remove markings that 
    won't be considered in ngram model. Also handle 
    multiple IPA entries (by only keeping the first).

    param: transcription, the original IPA string
    returns: cleaned, the cleaned IPA string
    """
    # Remove backslashes, stress accents
    cleaned = transcription.replace("/ ","").replace("ˈ ","").replace("ˌ ","")

    # Rewrite ":" as IPA character "ː"
    cleaned = cleaned.replace(":","ː")

    # Ignore tonal accents
    for accent in ACCENTS:
        if accent in cleaned:
            cleaned = cleaned.replace(" "+accent,"")

    # Only keep first IPA form
    ipa_forms = cleaned.split(",")
    if len(ipa_forms) > 1:
        cleaned = ipa_forms[0]
    
    return cleaned

# Initialize IPA dictionaries for all languages
def init_ipa_dictionary(language):
    """
    Create dictionary object using IPA dictionary CSV files.

    param: language, the string language abbreviation
    returns: ipa_dict, the dictionary of string word : string IPA transcription(s) pairs
    """
    # IPA CSV file path 
    #ipa = IPA_PATH + languages[language]["ipa_csv"]
    ipa = IPA_PATH + language + ".csv"

    # Initialize IPA dictionary
    ipa_dict = {}

    # Read and store IPA csv into dictionary
    with open(ipa, "r", encoding="utf-8", newline="") as ipa_csv:
        
        # Skip heading
        heading = next(ipa_csv)
        # Read each entry
        ipa_reader = csv.reader(ipa_csv)
        for line in ipa_reader:
            entry = line
            token = entry[0].lower()
            transcription = "".join(entry[1:]) # make it a string
            
            # Clean transcription
            transcription = clean_ipa(transcription)

            # Add token-transcription pair to dictionary
            ipa_dict[token] = transcription
    
    # Add dictionary object to global variable
    languages[language]["ipa_dict"] = ipa_dict
    
    return ipa_dict



"""
Conversion functions
"""

def tokenize_sentences(sentences, language="en"):
    """
    Tokenize each sentence in a list of sentences, based on the given language.

    param: sentences, a list of string sentences
    param: language, a string language acronym, 
                    default "en" for English and Latin alphabet languages
    returns: tokens_list, a list of string tokens t for each sentence s (a txs sized array)
    """
    tokens_list = []

    # Use a different method to tokenize Cantonese
    if language=="yue": 
        for s in sentences:
            result = jieba.tokenize(s)
            tokens = [tk[0] for tk in result]
            tokens_list.append(tokens)

    # Tokenize each sentence for all other languages
    else:
        for s in sentences:
            tokens = nltk.tokenize.word_tokenize(s)
            tokens_list.append(tokens)
        
    return tokens_list

def contains_letter(string):
    """
    Checks whether a string contains a letter character.
    Returns True if so, else False.

    param: string, the string to check
    return: True if string contains a letter char, else False
    """
    for char in string:
        if char.isalpha():
            return True
    
    return False

def similar_word_ipa(token, ipa_dict, lang):
    """
    Builds an IPA transcription by recursively looking for similar
    tokens in the ipa_dict. 

    param: token, the string token
    param: ipa_dict, the dictionary ipa dictionary for the given language
    param: lang, the string language abbreviation in use
    return: ipa, the string of ipa characters found, or "" if none found

    Example: for "yue", token:'人格尊严' returns ipa:'j ɐ n   k aː k   t s ɵ n   ',
             (concatenating first 3 individual pronunciations)
    
    Note: For Cantonese and other logographic languages,
    can trim tokens to a single character. For all other
    languanges, only looks at trimmed tokens > 1 char.
    """
    ipa = ""
    for i in range(len(token),-1,-1):
        trimmed = token[:i]

        # Note: only allow logographic languages to be trimmed to a single char
        if trimmed in ipa_dict and (len(trimmed)>1 or lang=="yue"):
            ipa += ipa_dict[trimmed]
            ipa += "   " if lang=="yue" else " " # for yue ipa-dict formatting

            ending = token.replace(trimmed,"",1)
            ipa += similar_word_ipa(ending, ipa_dict, lang)
            
            return ipa # Return IPA here, since further trims aren't needed

    return ipa

def contains_word_ipa(token, ipa_dict, lang):
    """
    Builds an IPA transcription by checking whether the token
    is contained in the starting text of the shortest similar 
    token in the ipa_dict. 
    
    Currently trims IPA of found token using an estimated 1-phoneme for 
    1-letter mapping.

    Note: that this does not guarantee accurate, only similar pronunciation!

    param: token, the string token
    param: ipa_dict, the dictionary ipa dictionary for the given language
    param: lang, the string language abbreviation in use
    return: (ipa, shortest), where: ipa, the string of IPA characters found, or "" if none found
                                    shortest, the word used to find similar IPA, or None if none found
    """
    ipa = ""
    possible = []
    for tok in ipa_dict.keys():
        if token in tok and tok.startswith(token):
            possible.append(tok)
    
    if possible: # If a containing token has been found
        shortest = min(possible, key = lambda x:len(x))
        diff = len(shortest) - len(token)
        ipa = ipa_dict[shortest][:-diff] # Assume, roughly, a 1-letter-1-phoneme mapping, and trim ipa by the difference in letters
        
        return (ipa, shortest)

    return (ipa, None)

def handle_unknown_tokens(token, ipa_dict, lang):
    """
    Handles a token not found in the ipa dictionary for a given language.
    Uses various methods.

    param: token, the string token
    param: ipa_dict, the dictionary ipa dictionary for the given language
    param: lang, the string language abbreviation in use 
    returns: found, the string IPA found. If no IPA found, returns empty string "".

    FUTURE: allow just a language abbrev. to be passed too.
    """
    found = ""

    # Only handle tokens that contain at least one letter
    if not contains_letter(token):
        return found

    # Case 1: Check hyphenated words
    if "-" in token:
        token_list = token.split("-")

        # Try joining hyphenated words
        joined = "".join(token_list)
        if joined in ipa_dict:
            found = ipa_dict[joined]
        
        # Try separating hyphenated words
        else:
            ipa = ""
            # Look for each new token
            for tok in token_list:
                # Concatenate transcriptions
                ipa += (ipa_dict[tok] + " ") if tok in ipa_dict else ""
            # If IPA was found for at least 1 separated token, add to found
            if ipa:
                found = ipa 
            
            # Else, skip this word
            else:
                unhandled_tokens[lang] += 1
                unhandled_tokens_list[lang].append(token)   
            
            return found

    # Case 2: Try a word stemmer from NLTK
    named_lang = NAMED_LANGS[lang]
    if named_lang in SnowballStemmer.languages:
        
        # Find stem of token
        stemmer = SnowballStemmer(named_lang)
        token_stem = stemmer.stem(token)

        # Add stem to IPA
        ipa = ""
        if token_stem in ipa_dict:
            ipa += ipa_dict[token_stem]
            
            # Look for suffix to add IPA
            suffix = token.replace(token_stem, "-", 1) # replace 1st occurrence with '-' to match ipa-dict suffix entries
            if suffix != token_stem and suffix in ipa_dict:
                ipa+= " " + ipa_dict[suffix]
                #FUTURE: allow a suffix to also be treated as a stem (make recursive) e.g. "-enen" for suffix "-en"

            found = ipa
            return(found)
        
    # Case 3: Try a similar-word pronunciation heuristic
    ipa = similar_word_ipa(token, ipa_dict, lang)
    if ipa:
        found = ipa
        return found

    # Case 4: Try a contains-word pronunciation heuristic
    ipa, similar = contains_word_ipa(token, ipa_dict, lang)
    if ipa:
        contains_word_cases[lang] += 1 # keeping track
        #print("HANDLED: "+token+", "+similar+", "+ipa)
        found = ipa
        return found

    # Else, skip this word and add to unhandled tokens list
    unhandled_tokens[lang] += 1
    unhandled_tokens_list[lang].append(token)   
    
    return found

# Evenly space out phoneme characters in a string of phonemes
def remove_extra_spaces(phonemes):
    """
    Removes extra spacing between a string of IPA characters.
    Returns the string with only one space between each character.

    param: phonemes, the string of phonemes
    return: pretty, the string of evenly spaced phonemes
    """
    chars = phonemes.split(" ")
    pretty = " ".join([c for c in chars if c and not c.isspace()])
    return pretty

# Transcribe sentence from text to IPA
def ipa_lookup(sent, lang, ipa_dict=None):
    """
    Look up IPA transcriptions for a given sentence (list of tokens).
    Return the sentence in IPA.

    param: sent, the list of word tokens in the given language
    param: lang, the string language abbreviation 
    param: ipa_dict, the dictionary object IPA dictionary for the language
                     (use lang to create, if no ipa_dict given)
    returns: phonemic_sent, the string sentence in phonemes
    """

    if not ipa_dict:
        ipa_dict = languages[lang]["ipa_dict"]
        if not ipa_dict:
            ipa_dict = init_ipa_dictionary(lang)
    
    phonemic_sent = ""

    # Look up IPA for each token
    for token in sent:
            
        # Handle unknown tokens
        if token not in ipa_dict:
            ipa = handle_unknown_tokens(token, ipa_dict, lang)
            
            if ipa: # if ipa found
                transcribed_tokens[lang] += 1
                #print("HANDLED TOKEN: " + token + ", " + ipa)
                
                for phoneme in ipa.split(" "):
                    phonemic_sent += phoneme + " "
        
        else:
            phonemic_sent += ipa_dict[token] + " "
            transcribed_tokens[lang] += 1
    
    if not phonemic_sent:
        unhandled_sents[lang] += 1

    # Evenly space phonemes and return sentence
    return remove_extra_spaces(phonemic_sent)

# Convert document from tokens to IPA for training
def convert(doc_path, language):
    """
    Convert document from natural language tokens 
    to phonemes in IPA characters using an IPA dictionary
    for the given language.

    Note: reads each line in document as a potential sentence. 

    param: doc_path, a string path to the document to be converted
    param: language, a string abbreviation for the document language

    Supported languages: 
    [] English (North American) (en)
    [] German (de)
    [] Spanish (es)
    [] French (fr)
    [] Italian (it)
    [] Korean (ko)
    [] Polish (pl)
    [] Portuguese (pt)
    [] Russian (ru)
    [] Turkish (tr)
    [] Cantonese (yue)
    """
    
    ipa_dict = init_ipa_dictionary(language)
    
    text_file = doc_path
    ipa_file = IPA_DOCS+language+"-doc-in-ipa-v2.txt"

    # Create new phoneme document
    with open(ipa_file, "w", encoding="utf-8") as phonemes:
        
        # Read in text document
        with open(text_file, "r", encoding="utf-8") as text:

            # Store sentences
            sentences = []
            for line in text: # Note: in training documents, each line is a 'sentence'.
                sentences.append(line.lower()) # Make all lowercase

        # Clean sentences
        cleaned_sents = []
        for s in sentences:

            # Remove newline characters and sentences that are only spaces
            if "\n" in s:
                new_sents = s.split("\n")
                sents = [sent for sent in new_sents if sent and not sent.isspace()]
                cleaned_sents.extend(sents)
            else:
                cleaned_sents.append(s)

        sentences = cleaned_sents
        #print(language,":", len(sentences), "sentences")

        # Tokenize each sentence and convert to IPA, then write to phoneme document
        tokenized_sents = tokenize_sentences(sentences, language)

        for sent in tokenized_sents:

            # Look up IPA transcription
            phonemic_sent = ipa_lookup(sent, language, ipa_dict)
            
            # Only write sentences with IPA found to phonemes document
            if phonemic_sent:
                #print(phonemic_sent)
                phonemes.write(remove_extra_spaces(phonemic_sent)+"\n")

# Convert all documents from tokens to IPA 
def convert_documents():
    """
    Convert all documents for training into IPA.
    """
    for lang in LANGUAGES:
        
        doc = DOCUMENT_PATH + languages[lang]["doc_file"]
        ipa = IPA_PATH + languages[lang]["ipa_csv"]

        convert(doc, lang)
    
    print("UNHANDLED SENTENCES:", unhandled_sents, "\n")
    print("UNHANDLED TOKENS:", unhandled_tokens, "\n")
    print("TRANSCRIBED TOKENS:", transcribed_tokens, "\n")
    print("Percent unhandled tokens:")
    for l in unhandled_tokens:
        percent = unhandled_tokens[l]/(unhandled_tokens[l]+transcribed_tokens[l])
        print(l + ":", percent)
    
    DEBUG=True
    if DEBUG:
        print("\nAll unique unhandled tokens:\n")
        for l in unhandled_tokens_list:
            unique_tokens = set(unhandled_tokens_list[l])
            print(l+" ( size =", len(unique_tokens), ")"+":",unique_tokens,"\n")

        print("\nNumber of tokens (including repeats) handled using contains-word heuristic:\n", contains_word_cases, "\n")


# Simple translate
def translate(sentence, lang, mode="fit"):
    """
    Translate a sentence in a given language from text to IPA characters.
    *Can be used for any sentence argument in a known language.*

    param: sentence, the string sentence
    param: lang, the string abbreviation for the sentence language
                 (call lookup_languages() to see a list of supported languages)
    param: mode, default "fit", mostly for unknown token handling.
                "fit": matches close-enough IPA using various methods
                "exact": returns only known IPA for specific tokens;
                         (this mode might not translate every word)
    return: phonemes, the string ipa transcription of the given sentence 
    """

    ipa_dict = languages[lang]["ipa_dict"]
    # Only initialize IPA dictionary once
    if not ipa_dict:
        ipa_dict = init_ipa_dictionary(lang)

    tokens = tokenize_sentences([sentence],lang)[0] # function takes list of sentences
                                                 # and returns list of list of tokens,
                                                 # so take 1st item

    if mode=="fit":
        return ipa_lookup(tokens, lang, ipa_dict)
    
    elif mode=="exact":
        phonemes = ""
        for tok in tokens:
            if tok in ipa_dict:
                phonemes += ipa_dict[tok] + " "
        return phonemes

def parse_ipa_input(ipa):
    """
    Clean and parse any string of IPA characters into parsed phonemes for ngram comparison.
    Returns a list of string phonemes.
    """
    # Remove punctuation from IPA, clean IPA
    ipa = re.sub(r'[^\w\s]', '', ipa) 
    ipa = clean_ipa(ipa)

    # Add IPA-informed spaces between phonemes 
    ipa = utilities.add_spaces_between_phonemes(ipa)

    phonemes = ipa.split() # Split into phonemes

    return phonemes



"""
RUN FUNCTIONS AS NEEDED:
"""
if __name__ == "__main__":
    # check_languages() 

    # Testing a single language
    # lang = "en"
    # doc = DOCUMENT_PATH + languages[lang]["doc_file"]
    # convert(doc, lang)
    # print("\nUnhandled tokens:", unhandled_tokens[lang])
    # print("\nContains word cases:", contains_word_cases[lang])
    # print("\nTranscribed tokens:", transcribed_tokens[lang])

    convert_documents()

    # print(translate("hi my friend", "en"))
    # print(translate("hi my fryend qui est vert", "en"))
    # print(translate("hi my fryend qui qui est vert", "en", mode="exact"))
    # print(text_to_ipa.translate("księżyc jest jasny","pl"))

