## Role

- user: human input/questions
- ai: model responses/answers
- system: instructions/context for the model

## Memory

AI models are stateless (no memory between requests), so external memory systems are needed

- sqlite Memory: persistent conversation history stored in database

## Context

background information or setting provided to the model

- Context window: maximum tokens the model can process at once (e.g., 4K, 8K, 128K tokens)
- Context length affects memory span and processing capability
- Longer context = more conversation history but higher computational cost

## Prompt Engineering Strategies

- few-shot
  In-Context Learning(ICL)

  ```
  Classify sentiment:
  "Great product!" → Positive
  "Poor quality" → Negative
  "I love this!" → ?
  ```

- role-based

  ```
  You are an expert data scientist.
  Analyze this dataset and provide insights...
  ```

- chain of thought

  Forces models to show step-by-step reasoning through prompting:

  ```
  Prompt: "Solve this step by step: What is 15% of 80?"

  Response: Let me think step by step:
  1. 15% = 15/100 = 0.15
  2. 0.15 × 80 = 12
  So 15% of 80 is 12.

  ```

  model-level reasoning:

  Built-in step-by-step like o1 thinking without special prompts  
  Automatically reason internally before responding

  Combine strategy:

  ```
  Prompt:
  Twitter is a social media platform where users post short messages called "tweets".
  Tweets can be positive or negative, and we want to classify them accurately. Here are some examples:
  Q: Tweet: "What a beautiful day!"
  A: positive
  Q: Tweet: "I hate this class"
  A: negative
  Q: Tweet: "I love pockets on jeans"
  A:

  Response: positive
  ```

- temperature and parameters

  ```
  temperature: 0.1 (focused, deterministic)
  temperature: 0.9 (creative, random)
  max_tokens: 150
  ```

## Tool

**Tooling**: AI models can be extended with external tools to perform actions beyond text generation

- api call: make HTTP requests to external services
- db query: interact with databases

## Vector

**Vector**: storing and searching text as high-dimensional numerical representations for semantic similarity

- chroma example: vector database for embeddings

  - Document chunking and embedding storage
  - Semantic search and similarity matching
  - RAG (Retrieval Augmented Generation) support
  - Persistent vector storage with metadata

- other vector databases:
  - Pinecone: managed vector database service
  - Weaviate: open-source vector search engine
  - Qdrant: vector similarity search engine
  - FAISS: Facebook's similarity search library

ref: https://learnprompting.org/docs/introduction
