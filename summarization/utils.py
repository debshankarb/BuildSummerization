import configparser
import spacy
import json
import re
from config import log_entry_exit

nlp_ner = spacy.load("en_core_web_sm")


class Utils:
    @log_entry_exit
    def process_response(strings):
        if len(strings) == 1:
            return strings[0]
        else:
            return ' '.join(strings)

    @log_entry_exit
    def preprocess_sentences(sentences):
        try:
            cleaned_sentences = []
            for sent in sentences:
                sent = sent.replace('(Work notes (internal))', '')
                sent = sent.replace('Ms-Team Chat--------------------------', '')
                sent = sent.replace('Sent from my iPhone', '')
                sent = sent.strip()
                cleaned_sentences.append(sent)
            return cleaned_sentences
        except Exception as e:
            raise Exception(f"Error during sentence preprocessing: {e}")

    @log_entry_exit
    def clean_text(worknote_list :list):
        '''
        Cleans text using spaCy NER and generates a summary using GenAI model.
        '''
        try:
            # Define the regular expression pattern with case-insensitive matching
            pattern = r"(?i)From:.*?Subject:"

            cleaned_chunks = []
            for worknote in worknote_list:
                # Remove everything between "From" and "Subject"
                worknote = re.sub(pattern, "Subject:", worknote, flags=re.DOTALL)

                # Process the text using spaCy NER
                doc = nlp_ner(worknote)

                # Create a list to store cleaned sentences
                cleaned_sentences = []

                # Iterate through sentences
                for sent in doc.sents:
                    cleaned_sentences.append(sent.text)

                # Preprocess the sentences
                preprocessed_sentences = Utils.preprocess_sentences(cleaned_sentences)

                # Join cleaned sentences to form cleaned text
                cleaned_text = "\n".join(preprocessed_sentences)
                cleaned_chunks.append(cleaned_text)

            return cleaned_chunks

        except Exception as e:
            # Handle exceptions during text cleaning and summarization
            raise Exception(f"Error during text cleaning: {e}")

    @log_entry_exit
    def extract_json_from_string(input):
        # Extract content within curly braces
        if isinstance(input, list):
            input = input[0]

        extracted_json = re.search(r'{(.+?)}', input, re.DOTALL)

        if extracted_json:
            return "{" + extracted_json.group(1) + "}"
        else:
            return None

    @log_entry_exit
    def convert_to_valid_json(json_like_string):
        # Extract JSON-like content
        json_content = Utils.extract_json_from_string(json_like_string)

        if json_content:
            try:
                data = json.loads(json_content)

                # Return JSON string with indentation
                return json.dumps(data, indent=4)
            except json.JSONDecodeError as e:
                raise Exception(e)
        else:
            return None
