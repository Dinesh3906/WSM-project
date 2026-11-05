"""
Module 5: Query Processor

Evaluates Boolean queries (AND, OR, NOT, AND NOT) and single-term queries using
set operations. Integrates with WildcardProcessor to resolve wildcard queries
and provides rich search metadata including filenames, snippets, and highlights.
"""
import time
import re
from typing import Dict, List, Set, Any, Tuple
from .inverted_index import InvertedIndex
from .wildcard_processor import WildcardProcessor
from .normalizer import normalize_token


class QueryProcessor:
    """
    Processes Boolean and wildcard retrieval queries against an InvertedIndex.
    Uses the Shunting-Yard algorithm and Reverse Polish Notation (RPN) evaluation
    with Python sets to execute Boolean algebra:
      - AND     -> Set Intersection (&)
      - OR      -> Set Union (|)
      - NOT     -> Set Difference from Universe (Universe - S)
      - AND NOT -> Direct Set Difference (A - B)
    """

    OPERATORS = {'AND', 'OR', 'NOT'}
    PRECEDENCE = {
        'NOT': 3,
        'AND': 2,
        'OR': 1
    }

    def __init__(self, inverted_index: InvertedIndex):
        """
        Initialize the query processor with an inverted index.

        :param inverted_index: An initialized InvertedIndex instance.
        """
        self.index = inverted_index
        self.wildcard_processor = WildcardProcessor()

    def tokenize_query(self, query_string: str) -> List[str]:
        """
        Tokenize a raw query string into terms, operators, and parentheses.
        Preserves wildcard asterisks '*' and recognizes Boolean keywords.

        :param query_string: User query.
        :return: List of tokens.
        """
        if not query_string or not isinstance(query_string, str):
            return []

        # Regex to capture parentheses as separate tokens or word/wildcard tokens
        raw_tokens = re.findall(r'\(|\)|\bAND\b|\bOR\b|\bNOT\b|[a-zA-Z0-9*]+', query_string, re.IGNORECASE)

        cleaned_tokens: List[str] = []
        for t in raw_tokens:
            upper_t = t.upper()
            if upper_t in self.OPERATORS or t in ('(', ')'):
                cleaned_tokens.append(upper_t)
            else:
                cleaned_tokens.append(normalize_token(t))

        return cleaned_tokens

    def _insert_implicit_and(self, tokens: List[str]) -> List[str]:
        """
        Insert implicit AND operators between adjacent terms or terms and '('
        when the user omits explicit operators (e.g., 'python search' -> 'python AND search').

        :param tokens: List of tokens.
        :return: Tokens with explicit ANDs inserted where needed.
        """
        if len(tokens) <= 1:
            return tokens

        result = []
        for i in range(len(tokens)):
            curr = tokens[i]
            result.append(curr)

            if i + 1 < len(tokens):
                nxt = tokens[i + 1]
                # Conditions where two consecutive tokens imply AND:
                # [TERM or ')'] followed by [TERM, 'NOT', or '(']
                curr_is_operand = curr not in self.OPERATORS and curr != '('
                nxt_is_operand = nxt not in {'AND', 'OR', ')'}

                if curr_is_operand and nxt_is_operand:
                    result.append('AND')

        return result

    def _shunting_yard(self, tokens: List[str]) -> List[str]:
        """
        Convert infix tokens to postfix (RPN) using Dijkstra's Shunting-Yard algorithm.

        :param tokens: List of normalized tokens in infix notation.
        :return: List of tokens in postfix notation.
        """
        output_queue: List[str] = []
        operator_stack: List[str] = []

        for token in tokens:
            if token in self.OPERATORS:
                while (
                    operator_stack
                    and operator_stack[-1] != '('
                    and self.PRECEDENCE.get(operator_stack[-1], 0) >= self.PRECEDENCE[token]
                ):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()  # discard '('
                else:
                    raise ValueError("Mismatched parentheses in query.")
            else:
                # Operand (search term or wildcard expression)
                output_queue.append(token)

        while operator_stack:
            top = operator_stack.pop()
            if top in ('(', ')'):
                raise ValueError("Mismatched parentheses in query.")
            output_queue.append(top)

        return output_queue

    def _resolve_term_postings(
        self, term: str, expanded_wildcards: Dict[str, List[str]]
    ) -> Set[str]:
        """
        Resolve a single query term to its set of matching document IDs.
        If term contains '*', expand using WildcardProcessor.

        :param term: Query term.
        :param expanded_wildcards: Dictionary to record any wildcard expansions.
        :return: Set of matching document IDs.
        """
        if self.wildcard_processor.is_wildcard(term):
            expanded_terms, postings = self.wildcard_processor.get_postings_for_wildcard(
                term, self.index
            )
            expanded_wildcards[term] = expanded_terms
            return postings
        else:
            return self.index.get_postings_set(term)

    def _evaluate_rpn(
        self, rpn_tokens: List[str], expanded_wildcards: Dict[str, List[str]]
    ) -> Set[str]:
        """
        Evaluate a Reverse Polish Notation (RPN) expression using Python set operations.

        :param rpn_tokens: Postfix token list.
        :param expanded_wildcards: Dictionary to record wildcard expansions.
        :return: Resulting set of document IDs.
        """
        eval_stack: List[Set[str]] = []
        all_docs = self.index.get_all_doc_ids()

        for token in rpn_tokens:
            if token == 'NOT':
                if not eval_stack:
                    # Unary NOT with empty preceding stack: evaluate as Universe
                    operand = set()
                else:
                    operand = eval_stack.pop()
                eval_stack.append(all_docs - operand)

            elif token == 'AND':
                if len(eval_stack) < 2:
                    raise ValueError("Invalid query: binary AND requires two operands.")
                right = eval_stack.pop()
                left = eval_stack.pop()
                eval_stack.append(left & right)

            elif token == 'OR':
                if len(eval_stack) < 2:
                    raise ValueError("Invalid query: binary OR requires two operands.")
                right = eval_stack.pop()
                left = eval_stack.pop()
                eval_stack.append(left | right)

            else:
                # Operand term
                postings = self._resolve_term_postings(token, expanded_wildcards)
                eval_stack.append(postings)

        if not eval_stack:
            return set()
        return eval_stack[-1]

    def _generate_snippet(self, content: str, query_terms: List[str], max_len: int = 240) -> str:
        """
        Generate a relevant snippet highlighting matching terms from the document text.

        :param content: Full document text.
        :param query_terms: Terms present in the query.
        :param max_len: Maximum length of snippet in characters.
        :return: Formatted snippet string.
        """
        if not content:
            return ""

        sentences = re.split(r'(?<=[.!?])\s+', content.strip())
        normalized_terms = [t.lower().replace('*', '') for t in query_terms if t not in self.OPERATORS]

        # Score sentences by number of matching terms
        best_sentence = sentences[0] if sentences else ""
        best_score = -1

        for sentence in sentences:
            score = 0
            low_sentence = sentence.lower()
            for term in normalized_terms:
                if term and term in low_sentence:
                    score += 1
            if score > best_score:
                best_score = score
                best_sentence = sentence

        # If best sentence is too long, truncate with ellipsis
        if len(best_sentence) > max_len:
            snippet = best_sentence[:max_len].rsplit(' ', 1)[0] + '...'
        else:
            snippet = best_sentence

        return snippet

    def process_query(self, query_string: str) -> Dict[str, Any]:
        """
        Main entry point for processing any query.
        Executes single-term, Boolean (AND, OR, NOT, AND NOT), and wildcard queries.

        :param query_string: Input search query string.
        :return: Detailed result dictionary.
        """
        start_time = time.perf_counter()
        expanded_wildcards: Dict[str, List[str]] = {}

        # 1. Validation for empty / whitespace query
        if not query_string or not query_string.strip():
            return {
                'query': query_string or '',
                'matching_doc_ids': [],
                'total_matching': 0,
                'expanded_wildcards': {},
                'documents': [],
                'parsed_tokens': [],
                'execution_time_ms': round((time.perf_counter() - start_time) * 1000, 3),
                'status': 'warning',
                'message': 'Query is empty. Please enter one or more search terms.'
            }

        # 2. Tokenize query
        tokens = self.tokenize_query(query_string)
        if not tokens:
            return {
                'query': query_string,
                'matching_doc_ids': [],
                'total_matching': 0,
                'expanded_wildcards': {},
                'documents': [],
                'parsed_tokens': [],
                'execution_time_ms': round((time.perf_counter() - start_time) * 1000, 3),
                'status': 'warning',
                'message': 'No valid alphanumeric search terms or operators found.'
            }

        # 3. Insert implicit ANDs between adjacent operands
        prepared_tokens = self._insert_implicit_and(tokens)

        # 4. Convert to RPN and evaluate
        try:
            rpn_tokens = self._shunting_yard(prepared_tokens)
            matching_ids_set = self._evaluate_rpn(rpn_tokens, expanded_wildcards)
        except Exception as e:
            return {
                'query': query_string,
                'matching_doc_ids': [],
                'total_matching': 0,
                'expanded_wildcards': expanded_wildcards,
                'documents': [],
                'parsed_tokens': prepared_tokens,
                'execution_time_ms': round((time.perf_counter() - start_time) * 1000, 3),
                'status': 'error',
                'message': f"Query syntax error: {str(e)}"
            }

        # Sort matching document IDs naturally (DOC1, DOC2, ...)
        def doc_sort_key(doc_id: str):
            digits = re.findall(r'\d+', doc_id)
            return int(digits[0]) if digits else doc_id

        sorted_doc_ids = sorted(list(matching_ids_set), key=doc_sort_key)

        # 5. Build rich document objects for the GUI
        matched_documents = []
        for doc_id in sorted_doc_ids:
            doc_meta = self.index.get_document_info(doc_id)
            content = doc_meta.get('content', '')
            snippet = self._generate_snippet(content, tokens)

            # Compute term frequencies in this document for the queried terms
            term_freqs = {}
            for t in tokens:
                if t not in self.OPERATORS and t not in ('(', ')'):
                    if self.wildcard_processor.is_wildcard(t):
                        # Sum frequencies of expanded terms
                        for exp_term in expanded_wildcards.get(t, []):
                            tf = self.index.get_term_frequency(exp_term, doc_id)
                            if tf > 0:
                                term_freqs[exp_term] = tf
                    else:
                        tf = self.index.get_term_frequency(t, doc_id)
                        if tf > 0:
                            term_freqs[t] = tf

            matched_documents.append({
                'doc_id': doc_id,
                'filename': doc_meta.get('filename', f"{doc_id}.txt"),
                'filepath': doc_meta.get('filepath', ''),
                'char_count': doc_meta.get('char_count', len(content)),
                'snippet': snippet,
                'term_frequencies': term_freqs
            })

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 3)

        status = 'success' if sorted_doc_ids else 'no_results'
        message = (
            f"Found {len(sorted_doc_ids)} matching document(s) in {execution_time_ms} ms."
            if sorted_doc_ids
            else f"No documents matched the query in {execution_time_ms} ms."
        )

        return {
            'query': query_string,
            'matching_doc_ids': sorted_doc_ids,
            'total_matching': len(sorted_doc_ids),
            'expanded_wildcards': expanded_wildcards,
            'documents': matched_documents,
            'parsed_tokens': prepared_tokens,
            'execution_time_ms': execution_time_ms,
            'status': status,
            'message': message
        }
