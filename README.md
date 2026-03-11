# AI Context Memory System

This project explores a simple idea: conversations with AI assistants often contain useful information about a project, but that information is difficult to reuse later.

When switching between tools like ChatGPT, Claude, or Gemini, the same context usually needs to be explained again. Important details such as design decisions, architecture explanations, or constraints get buried inside past chats.

The goal of this project is to extract useful knowledge from those conversations and make it reusable. Instead of repeating the same explanations, the system stores relevant information and retrieves it when needed.


## What the system does

The system reads AI conversations and extracts information that is likely to remain useful later. Examples include architecture notes, design decisions, and explanations of how parts of the project work.

This information is stored as structured memory entries. When a user asks a question about the project, the system searches those stored entries and builds a prompt containing the most relevant context.

The generated prompt can then be pasted into any AI assistant so that the assistant already understands the project background.


## Example

User question:

How does the memory extraction engine work?

The system retrieves related memory entries from previous conversations and produces a prompt containing that context. The prompt can then be given to an AI assistant to answer the question with the relevant project knowledge included.


## Main components

Conversation ingestion  
Imports conversations from AI share links and converts them into structured text data.

Memory extraction  
A local language model is used to identify information that should be kept as project knowledge.

Memory storage  
Extracted knowledge is stored in a structured format as memory packets.

Vector index  
Embeddings are created for each memory packet and stored in a FAISS index for semantic search.

Retrieval  
User queries are converted into embeddings and matched against stored memory packets.

Prompt generation  
Relevant memory entries are combined into a prompt that can be used with any AI assistant.


## Project structure

src/  
    ingestion  
    extraction  
    retrieval  
    prompt_generation  
    llm  
    utils  

data/  
    raw_conversations  
    projects/  
        ai_context_memory_system/  
            memory_packets.json  
            vector_index/  

scripts/


## Technologies used

Python  
Ollama  
Llama 3.1 (8B Q4)  
Sentence Transformers  
FAISS  
Playwright


## Running the project

Install dependencies

pip install -r requirements.txt

Build the vector index

python -m scripts.build_index

Test retrieval

python -m scripts.test_retrieval

Generate prompts

python -m scripts.test_prompt_generation


## Possible extensions

Support multiple projects  
Improve retrieval with topic filtering  
Add a simple web interface  
Experiment with different embedding models


## License

MIT License