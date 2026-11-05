"""
tests/test_search.py — Automated Test Suite for the Information Retrieval System

Tests cover:
  - Document loading
  - Tokenization
  - Case folding / normalization
  - Inverted index construction
  - Single-term search
  - AND, OR, NOT, AND NOT operations
  - Prefix, suffix, and infix wildcard queries
  - No-match queries
  - Invalid and empty queries
"""
import os
import sys
import unittest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DOCUMENTS_DIR
from modules.document_loader import DocumentLoader
from modules.tokenizer import Tokenizer, tokenize
from modules.normalizer import Normalizer, normalize_tokens, normalize_text
from modules.inverted_index import InvertedIndex
from modules.query_processor import QueryProcessor
from modules.wildcard_processor import WildcardProcessor


class TestDocumentLoader(unittest.TestCase):
    """Tests for Module 1: Document Loader."""

    def setUp(self):
        self.loader = DocumentLoader(DOCUMENTS_DIR)
        self.docs = self.loader.load_documents()

    def test_documents_loaded(self):
        """At least one document should be loaded from the documents directory."""
        self.assertGreater(len(self.docs), 0, "No documents loaded.")

    def test_twenty_documents_present(self):
        """The sample collection should contain twenty documents."""
        self.assertEqual(len(self.docs), 20)

    def test_documents_follow_natural_filename_order(self):
        """Document IDs should match the natural filename sequence."""
        filenames = [metadata['filename'] for metadata in self.docs.values()]
        self.assertEqual(filenames, [f'doc{number}.txt' for number in range(1, 21)])

    def test_document_ids_assigned(self):
        """Each document should have a DOC<n> identifier."""
        for doc_id in self.docs:
            self.assertTrue(doc_id.startswith("DOC"))

    def test_document_has_content(self):
        """Every loaded document should have non-empty content."""
        for doc_id, meta in self.docs.items():
            self.assertIn('content', meta)
            self.assertGreater(len(meta['content'].strip()), 0,
                               f"{doc_id} has empty content.")

    def test_document_has_filename(self):
        """Each document should store its original filename."""
        for doc_id, meta in self.docs.items():
            self.assertIn('filename', meta)
            self.assertTrue(meta['filename'].endswith('.txt'))

    def test_missing_directory(self):
        """Loading from a non-existent directory should return empty dict."""
        loader = DocumentLoader('/nonexistent/path')
        docs = loader.load_documents()
        self.assertEqual(len(docs), 0)


class TestTokenizer(unittest.TestCase):
    """Tests for Module 2: Tokenizer."""

    def setUp(self):
        self.tok = Tokenizer()

    def test_basic_tokenization(self):
        """Simple sentence should produce word tokens."""
        result = self.tok.tokenize("Hello World")
        self.assertEqual(result, ["Hello", "World"])

    def test_punctuation_removal(self):
        """Punctuation should be stripped from tokens."""
        result = self.tok.tokenize("Python, Flask! Data-structures.")
        self.assertIn("Python", result)
        self.assertIn("Flask", result)
        self.assertNotIn(",", result)
        self.assertNotIn("!", result)

    def test_empty_input(self):
        """Empty string should return an empty list."""
        self.assertEqual(self.tok.tokenize(""), [])

    def test_none_input(self):
        """None input should return an empty list."""
        self.assertEqual(self.tok.tokenize(None), [])

    def test_numbers_preserved(self):
        """Numeric tokens should be preserved."""
        result = self.tok.tokenize("Python 3 version 11")
        self.assertIn("3", result)
        self.assertIn("11", result)

    def test_convenience_function(self):
        """The module-level tokenize() function should work identically."""
        result = tokenize("web search engine")
        self.assertEqual(result, ["web", "search", "engine"])


class TestNormalizer(unittest.TestCase):
    """Tests for Module 3: Case Folding / Normalization."""

    def test_case_folding(self):
        """Uppercase tokens should be folded to lowercase."""
        tokens = ["Python", "SEARCH", "DaTa"]
        result = normalize_tokens(tokens)
        self.assertEqual(result, ["python", "search", "data"])

    def test_whitespace_stripping(self):
        """Tokens with leading/trailing whitespace should be trimmed."""
        tokens = ["  hello  ", " world "]
        result = normalize_tokens(tokens)
        self.assertEqual(result, ["hello", "world"])

    def test_empty_tokens_removed(self):
        """Empty or whitespace-only tokens should be removed."""
        tokens = ["good", "", "  ", "data"]
        result = normalize_tokens(tokens)
        self.assertEqual(result, ["good", "data"])

    def test_normalize_text(self):
        """Full text normalization should lowercase and collapse whitespace."""
        text = "  PYTHON   is   GREAT  "
        result = normalize_text(text)
        self.assertEqual(result, "python is great")

    def test_none_input(self):
        """None input should return empty list / empty string."""
        self.assertEqual(normalize_tokens(None), [])
        self.assertEqual(normalize_text(None), "")

    def test_consistency(self):
        """Document term and query term should normalize to the same value."""
        doc_token = Normalizer.normalize_token("Search")
        query_token = Normalizer.normalize_token("SEARCH")
        self.assertEqual(doc_token, query_token)


class TestInvertedIndex(unittest.TestCase):
    """Tests for Module 4: Inverted Index Construction."""

    def setUp(self):
        self.loader = DocumentLoader(DOCUMENTS_DIR)
        self.docs = self.loader.load_documents()
        self.index = InvertedIndex()
        self.index.build_index(self.docs)

    def test_vocabulary_not_empty(self):
        """The vocabulary should contain terms after indexing."""
        vocab = self.index.get_vocabulary()
        self.assertGreater(len(vocab), 0)

    def test_term_in_index(self):
        """Common terms should appear in the index."""
        postings = self.index.get_postings("python")
        self.assertGreater(len(postings), 0, "'python' not found in index.")

    def test_no_duplicate_doc_ids(self):
        """Postings list for any term should have unique document IDs."""
        for term in self.index.get_vocabulary():
            postings = self.index.get_postings(term)
            self.assertEqual(len(postings), len(set(postings)),
                             f"Duplicate doc IDs for term '{term}'.")

    def test_term_frequency_positive(self):
        """Term frequency should be at least 1 for indexed terms."""
        postings = self.index.get_postings("python")
        for doc_id in postings:
            tf = self.index.get_term_frequency("python", doc_id)
            self.assertGreaterEqual(tf, 1)

    def test_case_insensitive_lookup(self):
        """Index lookup should be case-insensitive."""
        lower = self.index.get_postings("search")
        upper = self.index.get_postings("SEARCH")
        self.assertEqual(lower, upper)

    def test_simple_dict_format(self):
        """to_simple_dict should return term -> [doc_ids] mapping."""
        simple = self.index.to_simple_dict()
        self.assertIsInstance(simple, dict)
        for term, doc_ids in simple.items():
            self.assertIsInstance(doc_ids, list)


class TestQueryProcessor(unittest.TestCase):
    """Tests for Module 5: Query Processing (AND, OR, NOT, AND NOT)."""

    def setUp(self):
        self.loader = DocumentLoader(DOCUMENTS_DIR)
        self.docs = self.loader.load_documents()
        self.index = InvertedIndex()
        self.index.build_index(self.docs)
        self.qp = QueryProcessor(self.index)

    # --- Single-Term ---
    def test_single_term(self):
        """A single-term query should return documents containing that term."""
        result = self.qp.process_query("python")
        self.assertEqual(result['status'], 'success')
        self.assertGreater(result['total_matching'], 0)

    # --- AND ---
    def test_and_query(self):
        """AND query should return intersection of two term postings."""
        result = self.qp.process_query("python AND search")
        # Must be a subset of each individual term's results
        r_python = set(self.qp.process_query("python")['matching_doc_ids'])
        r_search = set(self.qp.process_query("search")['matching_doc_ids'])
        r_and = set(result['matching_doc_ids'])
        self.assertTrue(r_and.issubset(r_python))
        self.assertTrue(r_and.issubset(r_search))

    # --- OR ---
    def test_or_query(self):
        """OR query should return union of two term postings."""
        result = self.qp.process_query("python OR data")
        r_python = set(self.qp.process_query("python")['matching_doc_ids'])
        r_data = set(self.qp.process_query("data")['matching_doc_ids'])
        r_or = set(result['matching_doc_ids'])
        self.assertEqual(r_or, r_python | r_data)

    # --- NOT ---
    def test_not_query(self):
        """NOT query should return documents that do NOT contain the term."""
        result = self.qp.process_query("NOT python")
        r_python = set(self.qp.process_query("python")['matching_doc_ids'])
        r_not = set(result['matching_doc_ids'])
        # No overlap with python's docs
        self.assertEqual(len(r_not & r_python), 0)

    # --- AND NOT ---
    def test_and_not_query(self):
        """AND NOT query should return A minus B."""
        result = self.qp.process_query("search AND NOT python")
        r_search = set(self.qp.process_query("search")['matching_doc_ids'])
        r_python = set(self.qp.process_query("python")['matching_doc_ids'])
        r_and_not = set(result['matching_doc_ids'])
        self.assertEqual(r_and_not, r_search - r_python)

    # --- No Match ---
    def test_no_match(self):
        """A term not in any document should return zero results."""
        result = self.qp.process_query("xyznonexistentterm")
        self.assertEqual(result['total_matching'], 0)
        self.assertIn(result['status'], ('no_results',))

    # --- Empty Query ---
    def test_empty_query(self):
        """An empty query should return a warning."""
        result = self.qp.process_query("")
        self.assertEqual(result['total_matching'], 0)
        self.assertEqual(result['status'], 'warning')

    # --- Invalid Query ---
    def test_whitespace_only_query(self):
        """A whitespace-only query should return a warning."""
        result = self.qp.process_query("   ")
        self.assertEqual(result['total_matching'], 0)
        self.assertEqual(result['status'], 'warning')


class TestWildcardProcessor(unittest.TestCase):
    """Tests for Module 6: Wildcard Processing."""

    def setUp(self):
        self.loader = DocumentLoader(DOCUMENTS_DIR)
        self.docs = self.loader.load_documents()
        self.index = InvertedIndex()
        self.index.build_index(self.docs)
        self.wp = WildcardProcessor()
        self.qp = QueryProcessor(self.index)
        self.vocab = self.index.get_vocabulary()

    def test_is_wildcard(self):
        """Strings containing '*' should be detected as wildcard terms."""
        self.assertTrue(self.wp.is_wildcard("comp*"))
        self.assertTrue(self.wp.is_wildcard("*tion"))
        self.assertTrue(self.wp.is_wildcard("inter*net"))
        self.assertFalse(self.wp.is_wildcard("python"))

    # --- Prefix wildcard ---
    def test_prefix_wildcard(self):
        """comp* should match terms starting with 'comp'."""
        matches = self.wp.expand("comp*", self.vocab)
        for m in matches:
            self.assertTrue(m.startswith("comp"),
                            f"'{m}' does not start with 'comp'")

    # --- Suffix wildcard ---
    def test_suffix_wildcard(self):
        """*tion should match terms ending with 'tion'."""
        matches = self.wp.expand("*tion", self.vocab)
        for m in matches:
            self.assertTrue(m.endswith("tion"),
                            f"'{m}' does not end with 'tion'")

    # --- Infix wildcard ---
    def test_infix_wildcard(self):
        """inter*net should match terms like 'internet'."""
        matches = self.wp.expand("inter*net", self.vocab)
        for m in matches:
            self.assertTrue(m.startswith("inter") and m.endswith("net"),
                            f"'{m}' does not match inter*net pattern")

    # --- Wildcard via query processor ---
    def test_wildcard_query_integration(self):
        """A wildcard query through QueryProcessor should expand terms and find docs."""
        result = self.qp.process_query("comp*")
        # Should have expanded_wildcards populated
        self.assertIn("comp*", result['expanded_wildcards'])

    # --- No expansion ---
    def test_wildcard_no_match(self):
        """A wildcard matching nothing should return zero results."""
        result = self.qp.process_query("zzzzz*")
        self.assertEqual(result['total_matching'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
