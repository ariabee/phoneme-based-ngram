# Phoneme-Based N-gram Language Identification
This project presents a phoneme-based n-gram language identification model that takes in a string of IPA (International Phonetic Alphabet) characters as input and identifies the language. Most likely languages are identified using an n-gram model trained on IPA-translated documents in 11 languages. The languages are scored using a method based on log probabilities of the input n-grams occurring in each language. To test the accuracy of the model, new sentences from each language are translated into IPA and identified. 

Results of this initial “snippet” test show that the model is accurate for 11/11 samples representing one sample for each language. 

This project offers additional functionalities:
1. transcribe a string of text (in 11 possible languages) into IPA characters

> `>>> translate("a transcribed phrase", "en")`</br>
>`'ə t ɹ æ n s k ɹ aɪ b d f ɹ eɪ z'`

> `>>> translate('綠色城市。', 'yue')` </br>
> `'l ʊ k s ɪ k s ɪ ŋ s iː'`

2. analyze frequency distributions of speech sounds across languages using the computed data from this project.
> *Initial work begins in `analyze.py`*.

## How to use

1. Install required packages: `pip install -r requirements.txt`

2. Open a command line interface.
Navigate to the project directory (this folder).

3. Run the following commands:

	`python3`
	
	`import finalproject, utilities, text_to_ipa, train_ngram, identify, evaluate`

	or

	`python3`

	`from finalproject import *`

