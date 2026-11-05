# WSM Assignment Report
## Modular Information Retrieval System

---

| Field | Details |
|-------|---------|
| **Student Name** | Dhavala Dinesh Kumar |
| **Roll Number** | B124043 |
| **Branch** | CSE-A |
| **Subject** | Web Search and Mining (WSM) |
| **Assignment** | Information Retrieval System |
| **Repository** | [github.com/Dinesh3906/WSM-project](https://github.com/Dinesh3906/WSM-project) |

---

## 1. Introduction

This report presents a complete, modular **Information Retrieval (IR) System** developed as part of the Web Search and Mining (WSM) course. The system demonstrates core IR concepts including document indexing, text preprocessing, inverted index construction, Boolean query processing, wildcard query expansion, and document retrieval — all served through a responsive web-based graphical user interface.

The project is implemented in **Python 3** using the **Flask** web framework and follows a clean modular architecture where each IR pipeline stage is encapsulated in a dedicated module.

---

## 2. Objectives

1. Understand and implement the document indexing pipeline (loading → tokenization → normalization → indexing).
2. Build an inverted index data structure mapping terms to document postings with term frequencies.
3. Implement Boolean query processing using set operations (AND, OR, NOT, AND NOT).
4. Support wildcard queries with prefix, suffix, and infix pattern matching.
5. Develop a user-friendly web GUI to demonstrate end-to-end search functionality.
6. Write automated tests to validate each module independently.

---

## 3. Technology Stack

| Component | Technology |
|-----------|------------|
| Programming Language | Python 3.11 |
| Web Framework | Flask 3.x |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Testing | Python unittest / pytest |
| Dependencies | Python standard library + Flask |

No external NLP libraries, databases, or search engines were used — the entire IR pipeline is implemented from scratch using Python's standard library.

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User (Web Browser)                    │
│                                                         │
│   ┌─────────────┐  ┌──────────┐  ┌──────────────────┐  │
│   │ Search Input │  │  Search  │  │ Read-Only Result │  │
│   │    Box       │  │  Button  │  │     Area         │  │
│   └──────┬──────┘  └────┬─────┘  └────────▲─────────┘  │
│          │              │                  │             │
└──────────┼──────────────┼──────────────────┼─────────────┘
           │   HTTP POST /search (JSON)      │ JSON Response
           ▼──────────────▼──────────────────┘
┌─────────────────────────────────────────────────────────┐
│                   Flask Backend (app.py)                 │
│                                                         │
│  ┌──────────────┐   ┌────────────┐   ┌───────────────┐  │
│  │  Document     │──▶│ Tokenizer  │──▶│  Normalizer   │  │
│  │  Loader       │   │            │   │ (Case Fold)   │  │
│  └──────────────┘   └────────────┘   └──────┬────────┘  │
│                                              │           │
│                                    ┌─────────▼────────┐  │
│                                    │  Inverted Index   │  │
│                                    │  Construction     │  │
│                                    └─────────┬────────┘  │
│                                              │           │
│  ┌──────────────┐   ┌────────────────────────▼────────┐  │
│  │  Wildcard     │◀──│    Query Processor              │  │
│  │  Processor    │──▶│  (Boolean + Wildcard Eval)      │  │
│  └──────────────┘   └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Execution Flow

1. **Startup:** `app.py` loads all documents, tokenizes them, normalizes tokens, and builds the inverted index.
2. **Query:** User types a query in the GUI → JavaScript sends a POST request to `/search`.
3. **Processing:** The query is tokenized, normalized, checked for wildcards, parsed into Boolean RPN, and evaluated using set operations against the inverted index.
4. **Response:** Matching document IDs, filenames, text snippets, wildcard expansions, and term frequencies are returned as JSON and rendered in the GUI.

---

## 5. Project Structure

```
WSM_Assignment/
│
├── app.py                      # Flask application entry point
├── config.py                   # Configuration (paths, server settings)
│
├── modules/
│   ├── __init__.py             # Package initialization
│   ├── document_loader.py      # Module 1: Document loading
│   ├── tokenizer.py            # Module 2: Tokenization
│   ├── normalizer.py           # Module 3: Text normalization
│   ├── inverted_index.py       # Module 4: Inverted index
│   ├── query_processor.py      # Module 5: Query processing
│   └── wildcard_processor.py   # Module 6: Wildcard handling
│
├── documents/                  # Corpus (5 sample documents)
│   ├── doc1.txt                # Python programming
│   ├── doc2.txt                # Information retrieval
│   ├── doc3.txt                # Search engines
│   ├── doc4.txt                # Data structures
│   └── doc5.txt                # Machine learning
│
├── templates/
│   └── index.html              # Frontend template
│
├── static/
│   ├── style.css               # Stylesheet
│   └── script.js               # Frontend logic
│
├── tests/
│   └── test_search.py          # 38 automated test cases
│
├── requirements.txt            # Dependencies
├── README.md                   # Project documentation
└── REPORT.md                   # This report
```

---

## 6. Module Descriptions

### 6.1 Module 1 — Document Loader (`document_loader.py`)

**Purpose:** Read all `.txt` files from the `documents/` directory and assign unique IDs.

**Key Features:**
- Scans the directory for `.txt` files with natural sort ordering (doc1, doc2, … doc10).
- Assigns sequential IDs: DOC1, DOC2, DOC3, …
- Stores filename, filepath, content, character count, and empty-file flag.
- Handles missing directories, non-existent paths, and empty files gracefully.

**Implementation:**
```python
class DocumentLoader:
    def load_documents(self) -> Dict[str, Dict[str, Any]]:
        # Scan directory → sort naturally → read each file
        # Returns: { "DOC1": { "filename": "doc1.txt", "content": "...", ... } }
```

### 6.2 Module 2 — Tokenizer (`tokenizer.py`)

**Purpose:** Split document content into individual word tokens.

**Key Features:**
- Uses regex pattern `[a-zA-Z0-9]+` to extract alphanumeric tokens.
- Automatically strips punctuation (commas, periods, exclamation marks, etc.).
- Returns a clean list of string tokens.
- Handles empty and None input safely.

**Example:**
```
Input:  "Python, Flask! Data-structures."
Output: ["Python", "Flask", "Data", "structures"]
```

### 6.3 Module 3 — Normalizer (`normalizer.py`)

**Purpose:** Case folding and whitespace normalization.

**Key Features:**
- Converts all tokens to lowercase (case folding).
- Strips leading/trailing whitespace from each token.
- Removes empty tokens.
- Applied consistently to both document terms AND user queries.

**Example:**
```
Input:  ["Python", "SEARCH", "  DaTa  "]
Output: ["python", "search", "data"]
```

**Why This Matters:** Without normalization, "Python" and "python" would be treated as different terms, causing missed search results.

### 6.4 Module 4 — Inverted Index (`inverted_index.py`)

**Purpose:** Construct a dictionary-based inverted index mapping terms to document postings.

**Key Features:**
- Internally calls the Tokenizer and Normalizer for each document.
- Maps each term to `{doc_id: term_frequency}`.
- Supports fast set-based lookups via `get_postings_set()`.
- No duplicate document IDs for any term.
- Tracks vocabulary, document frequencies, and term frequencies.

**Data Structure:**
```python
{
    "python":      {"DOC1": 4, "DOC5": 2},
    "search":      {"DOC1": 1, "DOC2": 1, "DOC3": 3},
    "information": {"DOC2": 3, "DOC3": 1, "DOC5": 2},
    ...
}
```

**Simplified View (as commonly shown in textbooks):**
```python
{
    "python":      ["DOC1", "DOC5"],
    "search":      ["DOC1", "DOC2", "DOC3"],
    "information": ["DOC2", "DOC3", "DOC5"]
}
```

### 6.5 Module 5 — Query Processor (`query_processor.py`)

**Purpose:** Parse and evaluate Boolean queries using set operations.

**Supported Operations:**

| Query Type | Example | Set Operation |
|------------|---------|---------------|
| Single term | `python` | Direct postings lookup |
| AND | `python AND search` | Set Intersection (A ∩ B) |
| OR | `python OR java` | Set Union (A ∪ B) |
| NOT | `NOT python` | Set Complement (U − A) |
| AND NOT | `search AND NOT python` | Set Difference (A − B) |

**Algorithm:**
1. **Tokenize** the query string (preserving operators AND, OR, NOT).
2. **Insert implicit ANDs** between adjacent terms (e.g., `python search` → `python AND search`).
3. **Convert to Reverse Polish Notation** using the Shunting-Yard algorithm.
4. **Evaluate RPN** using a stack with Python set operations.

**Example — `python AND search`:**
```
Tokenize:    ["python", "AND", "search"]
RPN:         ["python", "search", "AND"]
Evaluate:    postings("python") ∩ postings("search")
Result:      {"DOC1"}  (documents containing both terms)
```

### 6.6 Module 6 — Wildcard Processor (`wildcard_processor.py`)

**Purpose:** Expand wildcard patterns against the indexed vocabulary.

**Supported Patterns:**

| Pattern | Type | Example Matches |
|---------|------|-----------------|
| `comp*` | Prefix | computer, computing, complexity, compiled |
| `*tion` | Suffix | information, tokenization, normalization |
| `inter*net` | Infix | internet |

**Algorithm:**
1. Detect `*` in the query term.
2. Convert wildcard pattern to a regex: `comp*` → `^comp.*$`
3. Match regex against every term in the vocabulary.
4. Return expanded terms and the union of their document postings.

### 6.7 Module 7 — Frontend GUI

**Purpose:** Provide a clean, responsive web interface for search.

**GUI Components:**
1. **Title:** "Information Retrieval System"
2. **Search Input Box:** Text field for entering queries.
3. **Search Button:** Submits the query to the backend.
4. **Clear Button:** Resets the search input and results.
5. **Status Bar:** Shows success/warning/error messages.
6. **Wildcard Expansion Box:** Displays expanded terms for wildcard queries.
7. **Result Cards:** Each matching document shown with:
   - Document ID (e.g., DOC1)
   - Filename (e.g., doc1.txt)
   - Relevant text snippet
   - Character count
   - Term frequency badges
8. **Summary Row:** Total matching documents and execution time.

**Key Properties:**
- Results area is **read-only** — users cannot edit search results.
- Communication uses **real backend API calls** via `fetch()` — no fake/mock data.
- Responsive design works on desktop and mobile.

---

## 7. Sample Dataset

Five documents covering overlapping topics to enable Boolean and wildcard testing:

| Document | Topic | Key Terms |
|----------|-------|-----------|
| doc1.txt | Python Programming | python, programming, web, applications, data, computer, search |
| doc2.txt | Information Retrieval | information, retrieval, inverted, index, tokenization, normalization, query |
| doc3.txt | Search Engines | search, engines, web, crawl, internet, query, ranking, wildcard |
| doc4.txt | Data Structures | data, structures, hash, search, algorithms, computer, internet |
| doc5.txt | Machine Learning | machine, learning, classification, python, search, text, information |

**Term Overlap Examples:**
- "python" → DOC1, DOC5
- "search" → DOC1, DOC2, DOC3, DOC4, DOC5
- "information" → DOC2, DOC3, DOC5
- "internet" → DOC3, DOC4
- "computer" → DOC1, DOC3, DOC4

---

## 8. Test Results

The project includes **38 automated test cases** organized into 6 test classes:

| Test Class | Module Tested | Tests | Status |
|------------|---------------|-------|--------|
| TestDocumentLoader | Document Loading | 6 | ✅ All Pass |
| TestTokenizer | Tokenization | 6 | ✅ All Pass |
| TestNormalizer | Case Folding | 6 | ✅ All Pass |
| TestInvertedIndex | Index Construction | 6 | ✅ All Pass |
| TestQueryProcessor | Boolean Queries | 8 | ✅ All Pass |
| TestWildcardProcessor | Wildcard Queries | 6 | ✅ All Pass |
| **Total** | | **38** | **✅ All Pass** |

### Tests Cover:
- ✅ Document loading (valid, empty, missing directories)
- ✅ Tokenization (basic, punctuation removal, edge cases)
- ✅ Case folding (uppercase→lowercase consistency)
- ✅ Inverted index (vocabulary, postings, term frequency, no duplicates)
- ✅ Single-term search
- ✅ AND operation (set intersection)
- ✅ OR operation (set union)
- ✅ NOT operation (set complement)
- ✅ AND NOT operation (set difference)
- ✅ Prefix wildcard (`comp*`)
- ✅ Suffix wildcard (`*tion`)
- ✅ Infix wildcard (`inter*net`)
- ✅ Queries with no matching documents
- ✅ Empty and invalid queries

---

## 9. How to Run

### Installation
```bash
git clone https://github.com/Dinesh3906/WSM-project.git
cd WSM-project
pip install -r requirements.txt
```

### Run the Application
```bash
python app.py
```
Then open **http://127.0.0.1:5000** in a browser.

### Run Tests
```bash
python -m pytest tests/test_search.py -v
```

---

## 10. Conclusion

This project successfully implements a complete Information Retrieval System covering all core WSM concepts:

1. **Document Processing Pipeline:** Loading → Tokenization → Normalization → Indexing
2. **Inverted Index:** Efficient dictionary-based structure with term frequencies
3. **Boolean Retrieval Model:** AND, OR, NOT, AND NOT using set algebra
4. **Wildcard Queries:** Prefix, suffix, and infix pattern matching via regex
5. **Web Interface:** Functional GUI communicating with the real backend
6. **Testing:** 38 comprehensive test cases validating every module

The modular architecture ensures each component has a single responsibility and can be understood, tested, and explained independently — making it suitable for academic demonstration and practical examination.

---

**Submitted by:** Dhavala Dinesh Kumar | **Roll No:** B124043 | **Branch:** CSE-A

**Subject:** Web Search and Mining (WSM)
