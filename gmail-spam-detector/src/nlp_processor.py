"""
Natural Language Processing Module

This module uses NLTK to process email text for feature extraction and analysis.
Provides tokenization, stemming, stopword removal, and n-gram extraction.

Techniques Used:
- Tokenization: Break text into individual words/tokens
- Stemming: Reduce words to root form (running -> run)
- Stop word removal: Remove common words (the, a, is, etc.)
- N-gram extraction: Find common phrases (bigrams, trigrams)
"""

import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from typing import List, Dict, Set

logger = logging.getLogger(__name__)


class NLPProcessor:
    """
    Natural Language Processing engine for email analysis.

    Provides text processing capabilities using NLTK including:
    - Tokenization (breaking text into words)
    - Stemming (reducing words to root form)
    - Stop word removal (removing common words)
    - N-gram extraction (finding common phrases)

    This enhances ML feature extraction by providing linguistic insights.
    """

    def __init__(self):
        """Initialize NLP processor and download required NLTK data."""
        try:
            # Download required NLTK datasets
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt_tab', quiet=True)

            self.stemmer = PorterStemmer()
            self.stop_words: Set[str] = set(stopwords.words('english'))

            logger.info("NLP Processor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLP Processor: {e}")
            raise

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into individual words.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens (words)

        Example:
            >>> nlp = NLPProcessor()
            >>> tokens = nlp.tokenize("Hello world!")
            >>> print(tokens)
            ['Hello', 'world', '!']
        """
        if not text:
            return []

        try:
            tokens = word_tokenize(text)
            return tokens
        except Exception as e:
            logger.error(f"Error tokenizing text: {e}")
            return []

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove common stopwords from token list.

        Stopwords are common words like 'the', 'a', 'is', 'and', etc.
        that don't add significant meaning to text analysis.

        Args:
            tokens: List of tokens to filter

        Returns:
            Filtered list without stopwords

        Example:
            >>> tokens = ['the', 'cat', 'is', 'on', 'the', 'mat']
            >>> filtered = nlp.remove_stopwords(tokens)
            >>> print(filtered)
            ['cat', 'mat']
        """
        if not tokens:
            return []

        filtered = [
            token.lower() for token in tokens
            if token.lower() not in self.stop_words and token.isalnum()
        ]

        return filtered

    def stem(self, tokens: List[str]) -> List[str]:
        """
        Reduce words to their root/stem form.

        Stemming normalizes different word forms to the same root.
        Example: running, runs, ran -> run

        Args:
            tokens: List of tokens to stem

        Returns:
            List of stemmed tokens

        Example:
            >>> tokens = ['running', 'runs', 'ran', 'run']
            >>> stemmed = nlp.stem(tokens)
            >>> print(stemmed)
            ['run', 'run', 'ran', 'run']
        """
        if not tokens:
            return []

        stemmed = [self.stemmer.stem(token.lower()) for token in tokens]
        return stemmed

    def extract_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """
        Extract n-grams (common phrases) from tokens.

        N-grams are contiguous sequences of n tokens.
        - Bigrams (n=2): pairs of words
        - Trigrams (n=3): triplets of words

        Args:
            tokens: List of tokens
            n: Size of n-gram (default: 2 for bigrams)

        Returns:
            List of n-grams as strings

        Example:
            >>> tokens = ['the', 'quick', 'brown', 'fox']
            >>> bigrams = nlp.extract_ngrams(tokens, 2)
            >>> print(bigrams)
            ['the quick', 'quick brown', 'brown fox']
        """
        if not tokens or n < 1 or len(tokens) < n:
            return []

        ngrams = [
            ' '.join(tokens[i:i+n]).lower()
            for i in range(len(tokens) - n + 1)
        ]

        return ngrams

    def analyze_text(self, text: str) -> Dict:
        """
        Comprehensive text analysis combining all NLP techniques.

        Performs tokenization, stemming, stopword removal, and n-gram extraction
        in one complete analysis.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with comprehensive text analysis including:
            - tokens: List of individual words
            - token_count: Number of tokens
            - stemmed: Stemmed versions of tokens
            - stopwords_removed: Tokens with stopwords filtered out
            - bigrams: Common 2-word phrases
            - trigrams: Common 3-word phrases
            - unique_tokens: Count of unique tokens
            - content_richness: Ratio of unique to total tokens

        Example:
            >>> nlp = NLPProcessor()
            >>> result = nlp.analyze_text("Click here to verify your account")
            >>> print(result['token_count'])
            6
            >>> print(len(result['bigrams']))
            5
        """
        if not text:
            return {
                'tokens': [],
                'token_count': 0,
                'stemmed': [],
                'stopwords_removed': [],
                'bigrams': [],
                'trigrams': [],
                'unique_tokens': 0,
                'content_richness': 0.0,
            }

        # Step 1: Tokenize
        tokens = self.tokenize(text)

        # Step 2: Remove stopwords
        filtered_tokens = self.remove_stopwords(tokens)

        # Step 3: Stem
        stemmed_tokens = self.stem(filtered_tokens)

        # Step 4: Extract n-grams
        bigrams = self.extract_ngrams(filtered_tokens, 2)
        trigrams = self.extract_ngrams(filtered_tokens, 3)

        # Step 5: Calculate statistics
        unique_tokens = len(set(stemmed_tokens))
        token_count = len(tokens)
        content_richness = unique_tokens / max(1, token_count)

        analysis = {
            'tokens': tokens,
            'token_count': token_count,
            'stemmed': stemmed_tokens,
            'stopwords_removed': filtered_tokens,
            'bigrams': bigrams,
            'trigrams': trigrams,
            'unique_tokens': unique_tokens,
            'content_richness': content_richness,
        }

        return analysis

    def extract_keywords_frequency(self, text: str, top_n: int = 10) -> List[tuple]:
        """
        Extract most frequent keywords from text.

        Useful for understanding dominant themes in email content.

        Args:
            text: Input text
            top_n: Number of top keywords to return

        Returns:
            List of (keyword, frequency) tuples, sorted by frequency

        Example:
            >>> nlp = NLPProcessor()
            >>> keywords = nlp.extract_keywords_frequency("buy buy buy click click verify", top_n=3)
            >>> print(keywords)
            [('buy', 3), ('click', 2), ('verify', 1)]
        """
        if not text:
            return []

        analysis = self.analyze_text(text)
        tokens = analysis['stemmed']

        # Count frequencies
        freq_dict = {}
        for token in tokens:
            freq_dict[token] = freq_dict.get(token, 0) + 1

        # Sort by frequency
        sorted_keywords = sorted(
            freq_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_keywords[:top_n]

    def calculate_text_statistics(self, text: str) -> Dict:
        """
        Calculate various text statistics for analysis.

        Args:
            text: Input text

        Returns:
            Dictionary with statistics:
            - word_count: Number of words
            - sentence_count: Approximate sentence count
            - avg_word_length: Average word length
            - character_count: Total characters

        Example:
            >>> stats = nlp.calculate_text_statistics("Hello world! How are you?")
            >>> print(stats['word_count'])
            5
        """
        if not text:
            return {
                'word_count': 0,
                'sentence_count': 0,
                'avg_word_length': 0.0,
                'character_count': 0,
            }

        analysis = self.analyze_text(text)
        tokens = analysis['tokens']
        word_count = analysis['token_count']

        # Approximate sentence count (split by . ! ?)
        sentence_count = len([t for t in tokens if t in ['.', '!', '?']])
        sentence_count = max(1, sentence_count)  # At least 1 sentence

        # Average word length
        words = [t for t in tokens if t.isalnum()]
        avg_word_length = sum(len(w) for w in words) / max(1, len(words))

        # Character count
        character_count = len(text)

        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'character_count': character_count,
        }
