"""
Module 2: Tokenizer

Responsible for splitting text into discrete word tokens and stripping away
punctuation and non-alphanumeric characters.
"""
import re
from typing import List


class Tokenizer:
    """
    Extracts alphanumeric word tokens from raw input text.
    """

    def __init__(self, token_pattern: str = r'[a-zA-Z0-9]+'):
        """
        Initialize the tokenizer.

        :param token_pattern: Regular expression pattern defining valid tokens.
                              Default: continuous sequences of letters and numbers.
        """
        self.regex = re.compile(token_pattern)

    def tokenize(self, text: str) -> List[str]:
        """
        Extract tokens from raw text string.

        :param text: Input string content.
        :return: List of string tokens without punctuation.
        """
        if not text or not isinstance(text, str):
            return []

        tokens = self.regex.findall(text)
        return tokens


# Global default tokenizer instance
_default_tokenizer = Tokenizer()


def tokenize(text: str) -> List[str]:
    """
    Convenience function using the default tokenizer.

    :param text: Raw text to be tokenized.
    :return: List of tokens.
    """
    return _default_tokenizer.tokenize(text)

