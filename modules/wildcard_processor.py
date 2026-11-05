"""
Module 6: Wildcard Processor

Supports pattern matching with the '*' operator, enabling prefix, suffix, and
infix wildcard queries against the indexed vocabulary.
"""
import re
from typing import List, Set, Tuple, Iterable
from .normalizer import normalize_token


class WildcardProcessor:
    """
    Handles wildcard pattern compilation, vocabulary expansion, and
    postings retrieval for prefix (*tion), suffix (comp*), and infix (inter*net) queries.
    """

    @staticmethod
    def is_wildcard(term: str) -> bool:
        """
        Check if a term contains the wildcard '*' character.

        :param term: Query term to inspect.
        :return: True if '*' is in term, False otherwise.
        """
        if not term or not isinstance(term, str):
            return False
        return '*' in term

    @staticmethod
    def wildcard_to_regex(wildcard_pattern: str) -> re.Pattern:
        """
        Convert a wildcard expression with '*' into a compiled regular expression.
        Properly escapes regex special characters while translating '*' to '.*'.

        Examples:
            'comp*'     -> '^comp.*$'
            '*tion'     -> '^.*tion$'
            'inter*net' -> '^inter.*net$'

        :param wildcard_pattern: Query pattern containing '*'.
        :return: Compiled regex Pattern.
        """
        normalized_pattern = normalize_token(wildcard_pattern)
        # Split on '*' and escape each segment safely
        segments = normalized_pattern.split('*')
        escaped_segments = [re.escape(seg) for seg in segments]
        regex_pattern = f"^{'.*'.join(escaped_segments)}$"
        return re.compile(regex_pattern, re.IGNORECASE)

    def expand(self, wildcard_term: str, vocabulary: Iterable[str]) -> List[str]:
        """
        Find all terms in the vocabulary that match the wildcard pattern.

        :param wildcard_term: Term containing '*'.
        :param vocabulary: Iterable of unique terms (e.g., from InvertedIndex).
        :return: Sorted list of matching vocabulary terms.
        """
        if not self.is_wildcard(wildcard_term):
            normalized = normalize_token(wildcard_term)
            return [normalized] if normalized in vocabulary else []

        pattern = self.wildcard_to_regex(wildcard_term)
        matches = [term for term in vocabulary if pattern.match(term)]
        return sorted(matches)

    def get_postings_for_wildcard(
        self, wildcard_term: str, inverted_index
    ) -> Tuple[List[str], Set[str]]:
        """
        Expand a wildcard term against the index vocabulary and compute the union
        of document IDs containing any of the expanded terms.

        :param wildcard_term: Query term containing '*'.
        :param inverted_index: An instance of InvertedIndex.
        :return: Tuple containing:
            1. List of expanded vocabulary terms.
            2. Set of matching document IDs.
        """
        vocabulary = inverted_index.get_vocabulary()
        expanded_terms = self.expand(wildcard_term, vocabulary)

        matching_docs: Set[str] = set()
        for term in expanded_terms:
            matching_docs.update(inverted_index.get_postings_set(term))

        return expanded_terms, matching_docs
