# ChromaDB Vector Database Example
# This script demonstrates how text documents are converted to vectors and stored
# for semantic search and retrieval-augmented generation (RAG)

import os

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from google.genai import types

chroma_client = chromadb.Client()
google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Create collection with embedding function
# The embedding function converts text to high-dimensional vectors (typically 768+ dimensions)
collection = chroma_client.create_collection(name="test", embedding_function=google_ef)

# Add test documents to the collection
# Each document gets converted to a vector representation for semantic similarity search
# Vector data structure in database:
# {
#   "id": "crystals",
#   "document": "The Zephyrian crystal mines...",
#   "embedding": [0.0234, -0.1456, 0.2789, ...], # 768+ dimensional vector
#   "metadata": {}
# }

collection.add(
    documents=[
        "The Zephyrian crystal mines of planet Nexarth produce blue crystals that power interstellar ships.",
        "Captain Vex discovered the ancient Korvak ruins on the third moon of Zeltron system.",
        "The Quantum Flux Engine uses rare Stellarium ore to achieve faster-than-light travel.",
        "Botanist Dr. Kira found that Luminous Moss grows only in the caves of Asteroid B-47.",
        "The Treaty of Galactic Peace was signed at the Omega Station in the year 2387.",
    ],
    ids=["crystals", "ruins", "engine", "moss", "treaty"],
)

# Query gets converted to vector and compared with stored document vectors using cosine similarity
results = collection.query(
    query_texts=["What powers spaceships in the galaxy?"],
    n_results=2,
)

# ============================================================================
# SIMPLIFIED 2D VECTOR EXAMPLE FOR UNDERSTANDING
# ============================================================================
# In reality, embeddings have 768+ dimensions, but here's a 2D example:
#
# Documents and their hypothetical 2D vectors:
# "spaceship power"     -> [0.9, 0.1]  (high on tech, low on nature)
# "crystal energy"      -> [0.8, 0.2]  (high on tech, some nature)
# "ancient ruins"       -> [0.1, 0.8]  (low on tech, high on history)
# "plant biology"       -> [0.2, 0.9]  (low on tech, high on nature)
#
# Query: "What powers spaceships?" -> [0.85, 0.15]
#
# Similarity calculation (cosine similarity):
# Query vs "spaceship power": cos_sim([0.85, 0.15], [0.9, 0.1]) = 0.98 (very similar)
# Query vs "crystal energy":  cos_sim([0.85, 0.15], [0.8, 0.2]) = 0.94 (similar)
# Query vs "ancient ruins":   cos_sim([0.85, 0.15], [0.1, 0.8]) = 0.21 (not similar)
# Query vs "plant biology":   cos_sim([0.85, 0.15], [0.2, 0.9]) = 0.31 (not similar)
#
# Result: Returns "spaceship power" and "crystal energy" as most relevant matches
# ============================================================================

print("Query 1 - Spaceship power sources:")
print(results)
print("\n" + "=" * 50 + "\n")

# Setup Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Prepare context from vector search results
context_documents = results["documents"][0]  # Get the retrieved documents
context = "\n".join(context_documents)

# Prepare contents for Gemini
contents = f"""Based on the following context from my knowledge base:

{context}

Please answer: What powers spaceships in the galaxy?"""

# Generate content config
generate_content_config = types.GenerateContentConfig(
    temperature=0.7,
    max_output_tokens=1000,
)

# Stream response from Gemini
print("Gemini AI Response:")
print("-" * 30)
stream = client.models.generate_content_stream(
    model="gemini-2.0-flash",
    contents=contents,
    config=generate_content_config,
)

for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)

print("\n")
