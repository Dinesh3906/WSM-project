"""
app.py — Flask Application Entry Point

Integrates all six backend modules and serves the frontend GUI.
Execution flow on startup:
  1. Load documents from the corpus directory
  2. Tokenize and normalize document contents
  3. Build the inverted index
  4. Serve the GUI and process search queries via a REST API
"""
import os
from flask import Flask, render_template, request, jsonify
from config import DOCUMENTS_DIR, TEMPLATES_DIR, STATIC_DIR, SERVER_HOST, SERVER_PORT, DEBUG
from modules.document_loader import DocumentLoader
from modules.inverted_index import InvertedIndex
from modules.query_processor import QueryProcessor

# ---------------------------------------------------------------------------
# Flask Application Setup
# ---------------------------------------------------------------------------
app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)

# ---------------------------------------------------------------------------
# Index Construction (runs once at startup)
# ---------------------------------------------------------------------------
print("=" * 60)
print("  Information Retrieval System — Starting Up")
print("=" * 60)

# Step 1: Load documents
loader = DocumentLoader(DOCUMENTS_DIR)
documents = loader.load_documents()

# Step 2 & 3: Tokenization and normalization happen inside index building
# Step 4: Construct the inverted index
inverted_index = InvertedIndex()
inverted_index.build_index(documents)

# Step 5–9: Query processing handled per request
query_processor = QueryProcessor(inverted_index)

print(f"  Vocabulary size : {len(inverted_index.get_vocabulary())} terms")
print(f"  Documents loaded: {len(documents)}")
print("=" * 60)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def home():
    """Serve the main search GUI."""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """
    Process a search query sent from the frontend.

    Expects JSON body: { "query": "<search string>" }
    Returns JSON with matching document IDs, filenames, snippets,
    wildcard expansions, and execution metadata.
    """
    data = request.get_json(silent=True)
    if not data or 'query' not in data:
        return jsonify({
            'query': '',
            'matching_doc_ids': [],
            'total_matching': 0,
            'expanded_wildcards': {},
            'documents': [],
            'parsed_tokens': [],
            'execution_time_ms': 0,
            'status': 'error',
            'message': 'No query provided. Send JSON with a "query" field.'
        }), 400

    query_string = data['query']
    result = query_processor.process_query(query_string)
    return jsonify(result)


@app.route('/index-info', methods=['GET'])
def index_info():
    """
    Return metadata about the current inverted index for diagnostics.
    """
    vocab = inverted_index.get_vocabulary()
    return jsonify({
        'total_documents': len(documents),
        'vocabulary_size': len(vocab),
        'documents': [
            {
                'doc_id': doc_id,
                'filename': meta.get('filename', ''),
                'char_count': meta.get('char_count', 0),
                'is_empty': meta.get('is_empty', False)
            }
            for doc_id, meta in sorted(documents.items())
        ]
    })


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
