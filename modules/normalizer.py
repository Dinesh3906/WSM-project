"""
Module 3: Text Normalizer / Case Folding

Ensures all tokens are processed into uniform lowercased representations with
excess whitespace eliminated, guaranteeing consistency between document terms
and search queries.
"""
from typing import List


class Normalizer:
    """
    Handles case folding and whitespace normalization for tokens and text strings.
    """

    @staticmethod
    def normalize_token(token: str) -> str:
        """
        Normalize a single token by stripping whitespace and converting to lowercase.

        :param token: Input token string.
        :return: Normalized lowercase token.
        """
        if not token or not isinstance(token, str):
            return ""
        return token.strip().lower()

    @staticmethod
    def normalize_tokens(tokens: List[str]) -> List[str]:
        """
        Normalize a list of tokens.

        :param tokens: List of raw tokens.
        :return: List of normalized, non-empty lowercase tokens.
        """
        if not tokens:
            return []

        normalized = []
        for t in tokens:
            norm = Normalizer.normalize_token(t)
            if norm:
                normalized.append(norm)

        return normalized

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize a full text string: trims whitespace, collapses redundant spaces,
        and converts to lowercase.

        :param text: Input text.
        :return: Cleaned, lowercased string.
        """
        if not text or not isinstance(text, str):
            return ""
        return " ".join(text.strip().lower().split())


# Convenience module-level aliases
normalize_token = Normalizer.normalize_token
normalize_tokens = Normalizer.normalize_tokens
normalize_text = Normalizer.normalize_text

