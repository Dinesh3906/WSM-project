"""
Modules package for the Information Retrieval System.
"""
from .document_loader import DocumentLoader, load_documents
from .tokenizer import Tokenizer, tokenize
from .normalizer import Normalizer, normalize_tokens, normalize_text
from .inverted_index import InvertedIndex
from .wildcard_processor import WildcardProcessor
from .query_processor import QueryProcessor

__all__ = [
    'DocumentLoader',
    'load_documents',
    'Tokenizer',
    'tokenize',
    'Normalizer',
    'normalize_tokens',
    'normalize_text',
    'InvertedIndex',
    'WildcardProcessor',
    'QueryProcessor',
]

