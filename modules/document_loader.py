"""
Module 1: Document Loader

Responsible for reading text files from the corpus directory, assigning unique
document IDs, storing document metadata, and handling file edge cases.
"""
import os
import re
from typing import Dict, Any


class DocumentLoader:
    """
    Loads text documents from a specified directory, assigning consistent
    document identifiers (e.g., DOC1, DOC2) to each file.
    """

    def __init__(self, documents_dir: str):
        """
        Initialize the loader with the directory path containing document files.

        :param documents_dir: Path to directory containing .txt files.
        """
        self.documents_dir = documents_dir

    def load_documents(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan and load all .txt files from the documents directory.

        :return: Dictionary mapping doc_id -> {
            'doc_id': str,
            'filename': str,
            'filepath': str,
            'content': str,
            'char_count': int,
            'is_empty': bool
        }
        """
        documents: Dict[str, Dict[str, Any]] = {}

        if not os.path.exists(self.documents_dir):
            print(f"[Warning] Documents directory '{self.documents_dir}' does not exist.")
            return documents

        if not os.path.isdir(self.documents_dir):
            print(f"[Warning] Path '{self.documents_dir}' is not a directory.")
            return documents

        # Find all .txt files
        raw_files = [
            f for f in os.listdir(self.documents_dir)
            if f.lower().endswith('.txt') and os.path.isfile(os.path.join(self.documents_dir, f))
        ]

        if not raw_files:
            print(f"[Info] No .txt files found in '{self.documents_dir}'.")
            return documents

        # Natural sort helper so doc1, doc2, doc10 sort numerically
        def natural_sort_key(filename: str):
            return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', filename)]

        sorted_files = sorted(raw_files, key=natural_sort_key)

        for index, filename in enumerate(sorted_files, start=1):
            filepath = os.path.join(self.documents_dir, filename)
            doc_id = f"DOC{index}"

            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                is_empty = len(content.strip()) == 0

                documents[doc_id] = {
                    'doc_id': doc_id,
                    'filename': filename,
                    'filepath': filepath,
                    'content': content,
                    'char_count': len(content),
                    'is_empty': is_empty
                }

                if is_empty:
                    print(f"[Notice] Document '{filename}' ({doc_id}) is empty.")

            except Exception as e:
                print(f"[Error] Failed to read '{filename}': {e}")

        print(f"[Success] Loaded {len(documents)} document(s) from '{self.documents_dir}'.")
        return documents


def load_documents(documents_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to instantiate DocumentLoader and load documents.

    :param documents_dir: Directory containing .txt files.
    :return: Loaded documents dictionary.
    """
    loader = DocumentLoader(documents_dir)
    return loader.load_documents()

