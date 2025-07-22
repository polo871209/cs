# AI Learning Repository

A hands-on project for learning artificial intelligence fundamentals through building a chat application with persistent memory.

## Core AI Components

### Roles in AI Conversations

- **user**: human input/questions
- **ai**: model responses/answers
- **system**: instructions/context that guide the model's behavior

### Memory Systems

AI models are stateless (no memory between requests), so external memory systems are needed:

- **Short-term Memory**: Current conversation context
- **Long-term Memory**: Persistent conversation history stored in database (SQLite in this project)
- **Working Memory**: Information the AI can access during a single response

### Context Understanding

Background information or setting provided to the model:

- **Context Window**: Maximum tokens the model can process at once (e.g., 4K, 8K, 128K tokens)
- **Context Length**: Affects memory span and processing capability
- **Trade-offs**: Longer context = more conversation history but higher computational cost

## Prompt Engineering: Communicating with AI

The art of crafting effective instructions to get desired outputs from AI models.

### Key Strategies

**Few-Shot Learning** - Teaching through examples:

```
Classify sentiment:
"Great product!" → Positive
"Poor quality" → Negative
"I love this!" → ?
```

**Role-Based Prompting** - Setting the AI's persona:

```
You are an expert data scientist.
Analyze this dataset and provide insights...
```

**Chain of Thought** - Encouraging step-by-step reasoning:

```
Prompt: "Solve this step by step: What is 15% of 80?"

Response: Let me think step by step:
1. 15% = 15/100 = 0.15
2. 0.15 × 80 = 12
So 15% of 80 is 12.
```

**Model-Level Reasoning** - Built-in step-by-step thinking (like OpenAI's o1):

- Automatically reasons internally before responding
- No special prompts needed

**Combined Strategy Example**:

```
Twitter is a social media platform where users post short messages called "tweets".
Tweets can be positive or negative, and we want to classify them accurately. Here are some examples:
Q: Tweet: "What a beautiful day!"
A: positive
Q: Tweet: "I hate this class"
A: negative
Q: Tweet: "I love pockets on jeans"
A: positive
```

**Temperature and Parameters** - Controlling AI behavior:

```
temperature: 0.1 (focused, deterministic)
temperature: 0.9 (creative, random)
max_tokens: 150 (response length limit)
```

## AI Tools and Extensions

**Tool Integration**: AI models can be extended with external capabilities beyond text generation.

### Common AI Tools

**API Calls**: Make HTTP requests to external services

- Weather APIs, news feeds, stock prices
- Social media platforms, databases
- Any web service with an API

**Database Operations**: Interact with data storage

- Query SQL databases
- Store and retrieve information
- Update records based on user requests

**File Operations**: Work with documents and media

- Read/write files, analyze documents
- Image processing, data analysis
- Content generation and editing

### This Project's Tools

- Weather API integration for real-time data
- SQLite database for conversation storage
- Rich terminal formatting for better UX

## Vector Databases and Embeddings

**Vectors**: Mathematical representations of text that capture semantic meaning.

### How It Works

1. **Text → Numbers**: Convert words/sentences into high-dimensional numerical arrays
2. **Semantic Similarity**: Similar meanings have similar vector values
3. **Search**: Find relevant information by comparing vector distances

### Vector Database Examples

**ChromaDB** (used in this project):

- Document chunking and embedding storage
- Semantic search and similarity matching
- RAG (Retrieval Augmented Generation) support
- Persistent vector storage with metadata

**Other Popular Options**:

- **Pinecone**: Managed vector database service
- **Weaviate**: Open-source vector search engine
- **Qdrant**: Vector similarity search engine
- **FAISS**: Facebook's similarity search library

### Real-World Applications

- **Chatbots**: Finding relevant information from knowledge bases
- **Search Engines**: Understanding user intent beyond keywords
- **Recommendation Systems**: Suggesting similar content
- **Document Analysis**: Finding related documents or passages

## Getting Started with This Project

This chat application demonstrates core AI concepts in practice:

### Prerequisites

- Python 3.13+
- Basic command line knowledge
- Text editor or IDE

### Setup Instructions

1. **Clone the repository**
2. **Install dependencies**: `uv sync`
3. **Get API key**: Obtain Google Gemini API key
4. **Run the app**: `just run` or `uv run main.py`

### What You'll Learn

- **Conversation Flow**: How AI maintains context across messages
- **Memory Systems**: Persistent chat history with SQLite
- **Prompt Engineering**: Crafting effective AI instructions
- **Tool Integration**: Extending AI with external capabilities
- **Vector Search**: Finding relevant information semantically

### Hands-On Experiments

1. **Try different prompts** - See how phrasing affects responses
2. **Test memory** - Reference earlier conversation parts
3. **Use tools** - Ask for weather information
4. **Explore parameters** - Modify temperature settings
5. **Analyze responses** - Notice patterns in AI behavior

## Learning Path for AI Beginners

### Phase 1: Fundamentals (Weeks 1-2)

- Understanding what AI is and isn't
- Basic terminology and concepts
- How language models work at a high level
- Running and experimenting with this chat app

### Phase 2: Practical Skills (Weeks 3-6)

- Prompt engineering techniques
- Understanding context and memory
- Tool integration and APIs
- Basic Python programming for AI

### Phase 3: Advanced Concepts (Weeks 7-10)

- Vector databases and embeddings
- RAG (Retrieval Augmented Generation)
- Fine-tuning and training concepts
- AI safety and ethics

### Phase 4: Building Projects (Weeks 11+)

- Create your own AI applications
- Integrate multiple AI services
- Deploy AI systems to production
- Contribute to open-source AI projects

## Additional Resources

### Essential Reading

- [Learn Prompting](https://learnprompting.org/docs/introduction) - Comprehensive prompt engineering guide
- [Anthropic's AI Safety Fundamentals](https://www.anthropic.com/safety) - Understanding AI safety
- [OpenAI's GPT Best Practices](https://platform.openai.com/docs/guides/gpt-best-practices) - Effective AI usage

### Practical Tutorials

- [LangChain Documentation](https://docs.langchain.com/) - Building AI applications
- [Hugging Face Course](https://huggingface.co/course/) - Machine learning fundamentals
- [Fast.ai](https://www.fast.ai/) - Practical deep learning

### Communities

- [r/MachineLearning](https://reddit.com/r/MachineLearning) - Latest research and discussions
- [AI Twitter/X Community](https://twitter.com/hashtag/AI) - Real-time updates and insights
- [Discord AI Communities](https://discord.com/) - Interactive learning and support

## Next Steps

1. **Complete the setup** and run your first conversation
2. **Experiment** with different prompting strategies
3. **Modify the code** to add new features
4. **Join communities** to connect with other learners
5. **Build something new** using what you've learned

Remember: AI is a rapidly evolving field. Stay curious, experiment often, and don't be afraid to break things while learning!

---

_This project serves as your practical introduction to AI development. Each concept here connects to real-world applications used by millions of people daily._
