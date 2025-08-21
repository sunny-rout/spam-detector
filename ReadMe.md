# spam-detector

A Python project for detecting spam messages using machine learning.

## Folder Structure

- `src/clean_text.py`: Provides the [`clean_text`](src/clean_text.py) function for preprocessing and cleaning text data (lowercasing, removing punctuation/numbers, stopword removal, lemmatization).
- `src/connect_server.py`: Handles connecting to an email server (IMAP) for retrieving emails.
- `src/read_email.py`: Reads emails from the server and processes them for spam detection.
- `src/read_email_hard.py`: (Optional) Contains alternate or experimental email reading logic.
- `src/__init__.py`: Initializes the package and imports main modules.

## Getting Started

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
2. Download NLTK corpora if prompted (for text cleaning).
3. Place your email credentials in a secure location (do not hardcode).
4. Run the main script to connect to your email and classify messages.

## Data

- `spam.csv`: Dataset containing labeled SMS messages (`ham` for non-spam, `spam` for spam).
- `spam_classifier.pkl`, `vectorizer.pkl`: Pre-trained model and vectorizer for spam detection.

## Usage

Import and use the modules in `src` to clean text, connect to your email server, and classify messages.

## License