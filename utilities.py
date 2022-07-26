"""
AriaRay Brown
June, 2022

[utilities]
[pre-process ipa dictionaries]
Task-specific scripts used in project
for processing and cleaning IPA dictionaries.

"""

import csv


# Debug flag
DEBUG = False

# Supported languages
LANGUAGES = ["en", "de", "es", "fr", "it",
            "ko", "pl", "ru", "tr", "yue", "en_uk"]

NAMED_LANGS = {"en":"english","de":"german","es":"spanish","fr":"french","it":"italian",
              "ko":"korean","pl":"polish","ru":"russian","tr":"turkish","yue":"cantonese","en_uk":"english_uk"}


# IPA diacritics should be counted with the IPA character to its right
# (Only stand-alone characters are included, as others will be split with
# their base character as a single character, e.g. "tˠ".)
DIACRITICS = "ːʰ˞ʷʲˠˤⁿˡʼʱʴˑ"

# English (US and UK) diphthongs in IPA. These should/can be treated as a single phoneme.
DIPHTHONGS = ["oʊ","aʊ","aɪ","eɪ","ɔɪ","əʊ","ɪə","eə"]

#FUTURE: German/other language diphthongs?

# Tonal level accents in IPA. Specifically relevant to tonal languages ("yue").
ACCENTS = ["꜒","꜓","꜔","꜕","꜖","˥","˦","˧","˨","˩"]

# Define file paths
DOCUMENT_PATH = "./language-texts/"
IPA_PATH = "./ipa-dictionaries/"



# Function to add spaces between phonemes
def add_spaces_between_phonemes(ipa_forms):
    """
    Add spaces between phonemes (IPA characters) to match ipa-dictionaries.
    Considers that diphthongs and diacritics should be part of a single phoneme.

    param: ipa_forms, a string of IPA transcriptions (1 or more, separated by ", ")
    return: spaced_ipa, a string of spaced phonemes (for each transcription,
                        separated by ", ")
    """
    ipa_forms = ipa_forms.split(", ")
    spaced_ipa_forms = []
    
    for form in ipa_forms:
        form_with_spaces = ""
    
        checked_i = [] # to keep track of diphthong 2nd character index

        for i in range(len(form)):
            if i not in checked_i:
                
                # Don't add a space before the first char and 
                # keep diacritic characters combined with chars to the left
                if len(form_with_spaces)==0 or form[i] in DIACRITICS:
                    form_with_spaces += form[i]
                
                # Look for diphthongs to keep combined
                elif form[i:i+2] in DIPHTHONGS:
                    diph = form[i:i+2]
                    form_with_spaces += " " + diph
                    checked_i.append(i+1)

                # Add a space before all other phonemes
                else:
                    form_with_spaces += " " + form[i]
        
        spaced_ipa_forms.append(form_with_spaces)
    
    # Return spaced transcriptions
    spaced_ipa = ", ".join(spaced_ipa_forms)
    return spaced_ipa

# Preprocess English IPA dictionary
def en_text_to_csv():
    """
    Convert text format North-American English CMU 
    dictionary into csv file to match other 
    IPA dictionaries used in project.
    """

    # Define path of text file
    TEXT = "./discarded-og-files/en-cmudict-0.7b-ipa.txt"

    # Initialize CSV file
    CSV = "./ipa-dictionaries/en-v2.csv"

    # Open text file for reading
    with open(TEXT, "r", encoding="utf-8") as text:

        # Open csv file for writing
        with open(CSV, "w", encoding="utf-8", newline="") as new_csv:
            csv_writer = csv.writer(new_csv)

            # Write heading to match other ipa-dictionaries
            csv_writer.writerow(["headword","pronunciation"])
            
            # For each entry, write to row in csv file
            for line in text:
                entry = line.split()
                token = entry[0]
                
                # Put multiple IPA transcriptions into one string
                ipa = entry[1:]
                ipa = "".join(ipa) # okay to do for len(ipa) == 1

                # Replace any occurences of "r" phoneme with accurate "ɹ"
                ipa = ipa.replace("r","ɹ")

                # Add spaces between phonemes for each transcription
                spaced_ipa = add_spaces_between_phonemes(ipa)
                
                # Write new entry to csv file
                new_entry = [token, spaced_ipa]
                entry = new_entry

                csv_writer.writerow(entry)

        print("\nCSV file written to folder.\n")

# Preprocess Cantonese IPA dictionary
def yue_csv_edit():
    """
    Edit the Cantonese IPA dictionary csv file
    to be more similar to formatting in other 
    IPA dictionaries used in project.
    """

    # Define path to CSV files
    CSV = "./ipa-dictionaries/yue.csv"
    UPDATED = "./ipa-dictionaries/yue-v2.csv"

    # Open csv file for reading
    with open(CSV, "r", encoding="utf-8", newline="") as yue:
        csv_reader = csv.reader(yue)
        
        #Open new csv file for writing
        with open(UPDATED, "w", encoding="utf-8", newline="") as yue_updated:
            csv_writer = csv.writer(yue_updated)

            # Remove forward slashes "/" from IPA and rewrite ":" as "ː"
            for line in csv_reader:
                if len(line) != 2:
                    print(line)
                ipa = line[1].replace("/","").replace(":", "ː") # IPA is listed second

                # Add spaces between IPA characters to match ipa-dictionaries
                ipa_forms = ipa.split(", ")
                spaced_ipa_forms = []
                for form in ipa_forms:
                    form_with_spaces = ""
                    
                    # Keep diacritic characters combined with chars to the left
                    for char in form:
                        if char in DIACRITICS or len(form_with_spaces)==0: # Don't add a space before the first char
                            form_with_spaces += char 
                        else:
                            form_with_spaces += " " + char      
                    spaced_ipa_forms.append(form_with_spaces)
                
                # Update IPA transcription
                new_ipa = ", ".join(spaced_ipa_forms)
                
                # Re-write to updated CSV file
                new_entry = [line[0], new_ipa]
                csv_writer.writerow(new_entry)
    
    print("\nCSV file written to folder.\n")

# Preprocess English-UK ("en_uk") IPA dictionary
def en_uk_csv_edit():
    """
    Edit the UK English IPA dictionary csv file
    to be more similar to formatting in other 
    IPA dictionaries used in project. 
    (In case this one is used.)
    """

    # Define path to CSV files
    CSV = "./ipa-dictionaries/en_uk.csv"
    UPDATED = "./ipa-dictionaries/en_uk-v2.csv"

    # Open csv file for reading
    with open(CSV, "r", encoding="utf-8", newline="") as en_uk:
        csv_reader = csv.reader(en_uk)
        
        #Open new csv file for writing
        with open(UPDATED, "w", encoding="utf-8", newline="") as updated:
            csv_writer = csv.writer(updated)

            # Remove forward slashes "/" from IPA and rewrite ":" as "ː"
            for line in csv_reader:
                if len(line) != 2:
                    print(line)
                ipa = line[1].replace("/","").replace(":", "ː") # IPA is listed second
                ipa = ipa.replace("\u200d", "") # remove "zero width joiner"

                # Add spaces between phonemes to match ipa-dictionaries
                spaced_ipa = add_spaces_between_phonemes(ipa)

                # Make all tokens lowercase for easier lookup
                token = line[0].lower()

                # Re-write to updated CSV file
                new_entry = [token, spaced_ipa]
                csv_writer.writerow(new_entry)
    
    print("\nCSV file written to folder.\n")

# Make all IPA dictionary words lowercase
def make_all_lowercase():
    """
    Make all tokens in IPA dictionaries lowercase, for easier lookup.
    """
    for l in LANGUAGES:

        # Define file paths
        ipa = "./discarded-og-files/pre-lowercase-ipa-dicts/" + l + ".csv"
        updated = IPA_PATH + l + "-v2.csv"

        # Open csv file for reading
        with open(ipa, "r", encoding="utf-8", newline="") as ipa:
            csv_reader = csv.reader(ipa)
            
            # Open new csv file for writing
            with open(updated, "w", encoding="utf-8", newline="") as updated:
                csv_writer = csv.writer(updated)

                # Make each token lowercase
                for entry in csv_reader:
                    token = entry[0].lower()
                    phonemes = "".join(entry[1:])

                    # Write updated entry to csv file
                    updated_entry = [token, phonemes] 
                    csv_writer.writerow(updated_entry)
        


# Run utility functions as needed:
if __name__ == "__main__":
    #yue_csv_edit()
    #en_text_to_csv()
    #make_all_lowercase()
    #en_uk_csv_edit()
    print(add_spaces_between_phonemes("ˈsɛmiːˈkoʊlən"))
    
