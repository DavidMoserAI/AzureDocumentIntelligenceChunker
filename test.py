import os
import json
from typing import List

from common.Document import Document


# Load the example document
file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "example.json")
with open(file_path) as document:
    doc: dict = json.load(document)

# Build the document tree
document_instance: Document = Document(doc)
document_instance.build_trees()

# Print all chunks
chunks: List[dict] = document_instance.get_chunks()
for chunk in chunks:
    print(chunk)
    print("\n====================\n")
