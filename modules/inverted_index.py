"""
Module 4: Inverted Index Construction

Constructs an inverted index mapping unique vocabulary terms to the documents
in which they occur, avoiding duplicate entries while tracking term frequencies.
"""
from typing import Dict, List, Set, Any
from .tokenizer import tokenize
from .normalizer import normalize_tokens


class InvertedIndex:
    """
    An Inverted Index implementation that maps vocabulary terms to postings lists
    and records term frequencies within each document.
    """

    def __init__(self):
        """
        Initialize an empty inverted index.
        Internal structure:
        {
            "term": {
                "doc_id": count,
                ...
            }
        }
        """
        # Term -> {DocID -> TermFrequency}
        self.index: Dict[str, Dict[str, int]] = {}

        # Cache of document metadata
        self.documents: Dict[str, Dict[str, Any]] = {}

        # Set of all indexed document IDs
        self.all_doc_ids: Set[str] = set()

        # Total tokens count per document
        self.doc_token_counts: Dict[str, int] = {}

    def build_index(self, documents: Dict[str, Dict[str, Any]]) -> None:
        """
        Build the inverted index from a collection of documents.

        :param documents: Dictionary returned by DocumentLoader.
        """
        self.clear()
        self.documents = documents

        for doc_id, doc_meta in documents.items():
            self.all_doc_ids.add(doc_id)
            content = doc_meta.get('content', '')

            # 1. Tokenize document text
            tokens = tokenize(content)

            # 2. Normalize tokens (case-folding, whitespace trimming)
            normalized_tokens = normalize_tokens(tokens)

            self.doc_token_counts[doc_id] = len(normalized_tokens)

            # 3. Populate inverted index postings and term frequencies
            for term in normalized_tokens:
                if term not in self.index:
                    self.index[term] = {}

                if doc_id not in self.index[term]:
                    self.index[term][doc_id] = 0

                self.index[term][doc_id] += 1

        print(f"[Success] Built inverted index with {len(self.index)} unique terms across {len(self.all_doc_ids)} documents.")

    def get_postings(self, term: str) -> List[str]:
        """
        Retrieve a sorted list of unique document IDs containing the given term.

        :param term: Query term (should be normalized).
        :return: List of document IDs (e.g. ['DOC1', 'DOC3']).
        """
        normalized_term = term.strip().lower()
        if normalized_term in self.index:
            return sorted(list(self.index[normalized_term].keys()))
        return []

    def get_postings_set(self, term: str) -> Set[str]:
        """
        Retrieve a set of unique document IDs containing the given term.
        Optimized for set-based Boolean query operations.

        :param term: Query term.
        :return: Set of document IDs.
        """
        normalized_term = term.strip().lower()
        if normalized_term in self.index:
            return set(self.index[normalized_term].keys())
        return set()

    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """
        Get the frequency of a term within a specific document.

        :param term: Query term.
        :param doc_id: Target document ID.
        :return: Count of occurrences.
        """
        normalized_term = term.strip().lower()
        if normalized_term in self.index and doc_id in self.index[normalized_term]:
            return self.index[normalized_term][doc_id]
        return 0

    def get_doc_frequency(self, term: str) -> int:
        """
        Get the number of documents in which the term appears.

        :param term: Query term.
        :return: Document frequency.
        """
        normalized_term = term.strip().lower()
        if normalized_term in self.index:
            return len(self.index[normalized_term])
        return 0

    def get_vocabulary(self) -> List[str]:
        """
        Get all unique vocabulary terms present in the index.

        :return: Sorted list of terms.
        """
        return sorted(list(self.index.keys()))

    def get_all_doc_ids(self) -> Set[str]:
        """
        Get the set of all indexed document IDs.

        :return: Set of all document IDs.
        """
        return set(self.all_doc_ids)

    def get_document_info(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieve document metadata for a given document ID.

        :param doc_id: Document ID.
        :return: Metadata dictionary or empty dict if not found.
        """
        return self.documents.get(doc_id, {})

    def to_simple_dict(self) -> Dict[str, List[str]]:
        """
        Return the inverted index as a clean dictionary mapping term -> [DOC_IDs],
        matching typical classroom and assignment presentations.

        Example:
        {
            "python": ["DOC1", "DOC3"],
            "search": ["DOC1", "DOC2"]
        }
        """
        return {
            term: sorted(list(postings.keys()))
            for term, postings in sorted(self.index.items())
        }

    def to_detailed_dict(self) -> Dict[str, Any]:
        """
        Return a detailed summary of the index with term frequencies.
        """
        result = {}
        for term, postings in sorted(self.index.items()):
            result[term] = {
                'doc_frequency': len(postings),
                'postings': sorted(list(postings.keys())),
                'term_frequencies': postings
            }
        return result

    def clear(self) -> None:
        """
        Reset the inverted index.
        """
        self.index.clear()
        self.documents.clear()
        self.all_doc_ids.clear()
        self.doc_token_counts.clear()

