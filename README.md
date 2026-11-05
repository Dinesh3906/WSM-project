# Information Retrieval System — WSM Assignment

A modular **Information Retrieval System** built with Python and Flask, demonstrating document indexing, text preprocessing, inverted index construction, Boolean query processing, wildcard query handling, and a web-based search GUI.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Document Loading | Reads `.txt` files from a corpus directory with unique document IDs |
| 2 | Tokenization | Splits text into alphanumeric tokens, stripping punctuation |
| 3 | Text Normalization | Case folding to lowercase and whitespace cleanup |
| 4 | Inverted Index | Maps vocabulary terms → document postings with term frequencies |
| 5 | Query Processing | Supports single-term, AND, OR, NOT, and AND NOT queries |
| 6 | Wildcard Queries | Prefix (`comp*`), suffix (`*tion`), and infix (`inter*net`) matching |
| 7 | Web GUI | Clean, responsive search interface with real-time backend results |

---

## Technology Stack

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **Libraries:** Python standard library only (+ Flask)

---

## Project Structure

```
WSM_Assignment/
│
├── app.py                      # Flask application entry point
├── config.py                   # Project configuration
│
├── modules/
│   ├── __init__.py             # Package initializer
│   ├── document_loader.py      # Module 1: Document loading
│   ├── tokenizer.py            # Module 2: Tokenization
│   ├── normalizer.py           # Module 3: Text normalization / case folding
│   ├── inverted_index.py       # Module 4: Inverted index construction
│   ├── query_processor.py      # Module 5: Query processing (Boolean)
│   └── wildcard_processor.py   # Module 6: Wildcard query handling
│
├── documents/                  # Sample text corpus
│   ├── doc1.txt                # Python programming
│   ├── doc2.txt                # Information retrieval
│   ├── doc3.txt                # Search engines
│   ├── doc4.txt                # Data structures
│   └── doc5.txt                # Machine learning
│
├── templates/
│   └── index.html              # Frontend HTML template
│
├── static/
│   ├── style.css               # Stylesheet
│   └── script.js               # Frontend JavaScript
│
├── tests/
│   └── test_search.py          # Automated test suite
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Dinesh3906/WSM-project.git
cd WSM-project

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Application

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## Module Descriptions

### Module 1 — Document Loader (`document_loader.py`)
Scans the `documents/` directory for `.txt` files, sorts them naturally, assigns sequential IDs (DOC1, DOC2, …), reads file contents, and handles missing/empty files gracefully.

### Module 2 — Tokenizer (`tokenizer.py`)
Uses regex pattern matching to extract sequences of alphanumeric characters from raw text, effectively removing punctuation and special characters.

### Module 3 — Normalizer (`normalizer.py`)
Performs case folding (converting all tokens to lowercase) and strips unnecessary whitespace. Applied identically to both documents and queries to ensure consistent matching.

### Module 4 — Inverted Index (`inverted_index.py`)
Builds a dictionary-based inverted index where each unique term maps to a postings dictionary of `{doc_id: term_frequency}`. Supports fast set-based retrieval for Boolean operations.

### Module 5 — Query Processor (`query_processor.py`)
Parses Boolean queries using the Shunting-Yard algorithm, converts them to Reverse Polish Notation, and evaluates using Python set operations (intersection for AND, union for OR, complement for NOT).

### Module 6 — Wildcard Processor (`wildcard_processor.py`)
Converts wildcard patterns (`*`) to regular expressions and matches against the indexed vocabulary. Supports prefix, suffix, and infix wildcards. Returns expanded terms and the union of their document postings.

### Module 7 — Frontend GUI (`templates/index.html`, `static/`)
A responsive web interface with a search input, Search/Clear buttons, and a read-only result area displaying matching document IDs, filenames, text snippets, wildcard expansions, and term frequencies.

---

## Sample Queries & Expected Behavior

| Query | Type | Expected Behavior |
|-------|------|-------------------|
| `python` | Single term | Returns all documents containing "python" |
| `python AND search` | AND | Returns documents containing both "python" and "search" |
| `python OR java` | OR | Returns documents containing either "python" or "java" |
| `NOT python` | NOT | Returns all documents that do NOT contain "python" |
| `search AND NOT python` | AND NOT | Returns documents with "search" but without "python" |
| `comp*` | Prefix wildcard | Expands to "computer", "computing", "complexity", etc. |
| `*tion` | Suffix wildcard | Expands to "information", "tokenization", "normalization", etc. |
| `inter*net` | Infix wildcard | Expands to "internet" |

---

## Running Tests

```bash
python -m pytest tests/test_search.py -v
```

Or using unittest directly:

```bash
python -m unittest tests.test_search -v
```

---

## License

This project was developed for academic purposes as part of a Web Search and Mining (WSM) course assignment.
