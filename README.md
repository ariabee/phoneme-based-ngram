# Phoneme-Based N-gram Language Identification
This phoneme-based n-gram language identification model takes in a string of IPA (International Phonetic Alphabet) characters as input and identifies the language. Most likely languages are identified using an n-gram model trained on IPA-translated documents in 11 languages. The languages are scored using a method based on log probabilities of the input n-grams occurring in each language. To test the accuracy of the model, new sentences from each language are translated into IPA and identified. 

Results of this initial “snippet” test show that the model is accurate for 11/11 samples representing one sample for each language. 

**This project offers additional functionalities:**
1. transcribe a string of text (in 11 possible languages) into IPA characters

	`translate("a transcribed phrase", "en")`</br>
	`'ə t ɹ æ n s k ɹ aɪ b d f ɹ eɪ z'`

	`translate('綠色城市。', 'yue')` </br>
	`'l ʊ k s ɪ k s ɪ ŋ s iː'`

2. analyze frequency distributions of speech sounds across languages using the computed data from this project.
	> *Analysis begins in `analyze.py`*.

This work began as an open-ended final project for the master's course "Computational Linguistics" at UdS.

## To-Do's

- organize project files into folders
- add revised Report.pdf
- add console gif :)



## How to Use

1. Open a command line interface. Clone the repository to your local machine.

2. Install required packages: `pip install -r requirements.txt`

3. Navigate to the project directory (this folder).

4. Run the following commands:

```
python3
import finalproject, utilities, text_to_ipa, train_ngram, identify, evaluate
```
or

```
python3
from finalproject import *
```

## Project Steps
This project was built in the following order:
1) `utilities.py`
2) `text_to_ipa.py`
3) `train_ngram.py`
4) `identify.py`
5) `evaluate.py`

### Fun Functions
Some functions can be used outside of this project. For example:
   - `text_to_ipa.translate()` # translate text in a given language into IPA characters
   - `identify.identify()` # estimate the language of a string of IPA characters

## Hello Note
Hello! Sometimes we're given opportunities to bring an idea to fruition, and sometimes the only way forward is to come up with an idea. This project is a result of both circumstances. The deed is done, the work was plenty, and now I'm happy to share this project here. 

To anyone interested, feel free to look around! And to anyone with an untold idea, I can attest that the bigger the unknown, the more rewarding the finish line. (That is, the first finish line, because we have to finish sometime. :) )

