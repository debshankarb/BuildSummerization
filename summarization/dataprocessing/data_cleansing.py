import re
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax


# Preprocess text
def preprocess_text(text):
    """
    Preprocesses the input text by stripping extra whitespace and reducing consecutive whitespace to a single space.
    """
    try:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text
    except Exception as e:
        # Handle exceptions during text preprocessing
        raise Exception(f"Error during text preprocessing: {e}")


# Chitchat removal using BERT
def remove_chitchat(text):
    """
    Uses BERT model for binary classification to determine if input text contains chitchat.
    """
    try:
        model_name = "bert-base-uncased"
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertForSequenceClassification.from_pretrained(
            model_name, num_labels=2)

        labels = ["non-chitchat", "chitchat"]
        inputs = tokenizer(text, return_tensors="pt",
                           padding=True, truncation=True)
        logits = model(**inputs).logits
        probabilities = softmax(logits, dim=1).detach().cpu().numpy()[0]

        predicted_label = labels[int(probabilities.argmax())]

        if predicted_label == "non-chitchat":
            return text
        else:
            return None
    except Exception as e:
        # Handle exceptions during chitchat removal
        raise Exception(f"Error during chitchat removal: {e}")


# Remove generic information
def remove_generic_info(text):
    """
    Removes generic information patterns from the input text using regular expressions.
    """
    try:
        # Customize the regex patterns to match different types of generic information
        patterns_to_remove = [
            r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",
            r"\(\d+\)",
            r"\[.*?\]",
            r"[-*]+",
            r"(\b[A-Z][a-z]*\b\s*)+\s*,",
            r"(@|c|\+[\d-]+|\(at\))\s*:\s*[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]+",
        ]

        for pattern in patterns_to_remove:
            text = re.sub(pattern, "", text)

        return text.strip()
    except Exception as e:
        # Handle exceptions during generic information removal
        raise Exception(f"Error during generic information removal: {e}")


def process_conversation_notes(text):
    """
    Processes conversation notes by preprocessing, removing generic information, and chitchat detection.
    """
    try:
        # Process conversation notes
        notes_lines = text.strip().split("\n")
        cleaned_notes = []

        for line in notes_lines:
            if line.strip():  # Ignore empty lines
                cleaned_line = preprocess_text(line)
                cleaned_line = remove_generic_info(cleaned_line)
                cleaned_chitchat_removed = remove_chitchat(cleaned_line)
                if cleaned_chitchat_removed:
                    cleaned_notes.append(cleaned_chitchat_removed)

        # Create a cleaned text document
        cleaned_text = "\n".join(cleaned_notes)

        return cleaned_text
    except Exception as e:
        # Handle exceptions during conversation notes processing
        raise Exception(f"Error during conversation notes processing: {e}")
