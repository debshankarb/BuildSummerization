import spacy
import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from config import log_entry_exit

# Load the spaCy NER model
nlp_ner = spacy.load("en_core_web_sm")

# Load BART model and tokenizer
model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

@log_entry_exit
def clean_text_with_ner(text):
    # Process the text using spaCy NER
    doc = nlp_ner(text)

    # Create a list to store cleaned sentences
    cleaned_sentences = []

    # Iterate through sentences
    for sent in doc.sents:
        # Initialize a list to store cleaned tokens
        cleaned_tokens = []

        # Iterate through tokens in the sentence
        for token in sent:
            # Keep relevant entities and non-punctuation tokens
            if token.ent_type_ or not token.is_punct:
                cleaned_tokens.append(token.text)

        # Join cleaned tokens to form cleaned sentence
        cleaned_sentence = " ".join(cleaned_tokens).strip()

        # Append cleaned sentence to the list
        if cleaned_sentence:
            cleaned_sentences.append(cleaned_sentence)

    # Join cleaned sentences to form cleaned text
    cleaned_text = "\n".join(cleaned_sentences)

    return cleaned_text

@log_entry_exit
def generate_summaries(worknote):
    cleaned_data_ner = clean_text_with_ner(worknote)

    inputs = tokenizer(
        cleaned_data_ner, max_length=1024, return_tensors="pt", truncation=True
    )
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=150,
        min_length=50,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True,
    )
    cleaned_summary = tokenizer.decode(
        summary_ids[0], skip_special_tokens=True)

    return cleaned_summary


@log_entry_exit
def bart_summarization(worknote: str):
    cleaned_summary = generate_summaries(worknote)
    return cleaned_summary
