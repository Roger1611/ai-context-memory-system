# AI Context Memory System

This project explores a simple idea: AI chats contain useful knowledge, but that knowledge disappears once the conversation ends.

When working on long projects with AI tools like ChatGPT or Claude, I often found myself repeating the same context again and again — explaining the project structure, previous decisions, or results from earlier experiments.

The goal of this project is to experiment with a small system that can capture useful information from AI conversations and store it as reusable project memory.

Instead of treating chats as temporary conversations, the system tries to extract durable information such as:

* project progress
* architecture decisions
* repository structure
* development commands
* research insights

That information is stored in structured “memory packets” and indexed so it can be retrieved later when working with another AI system.

The idea is that a project’s context can slowly accumulate over time instead of being lost between chats.

---

## What the System Does

At a high level the system takes an AI conversation and tries to turn it into reusable knowledge.

1. A share link to an AI chat is provided.
2. The conversation is downloaded and parsed.
3. A local LLM analyzes the text and extracts useful project information.
4. The extracted knowledge is stored as structured memory packets.
5. Embeddings are generated so the information can be searched later.
6. A project snapshot summarizing the current state of the project can be generated.

The final snapshot can be pasted into another AI conversation to quickly restore project context.

---

## Example of Stored Memory

Information from conversations is stored as small JSON packets.

Example:

```id="ex2f7b"
{
  "project": "EEG Representation Geometry",
  "topic": "architecture",
  "type": "decision",
  "content": "DeepConvNet was selected as the main backbone for the representation study.",
  "source_conversation": "bf1b280b.json"
}
```

Each packet captures a small piece of project knowledge that may be useful later.

---

## Project Structure

```id="j3fsn9"
ai-context-memory-system/

memory_sync.py

src/
  ingestion/
  extraction/
  retrieval/
  utils/

memory/
  packets/
  vector_index/

examples/
```

The main pipeline is executed through `memory_sync.py`.

Most of the logic is split across modules inside the `src` directory.

---

## Technologies Used

Python
Playwright (for fetching share links)
Ollama for local LLM inference
Qwen2.5-7B-Instruct
HuggingFace embedding models
FAISS for vector search

---

## Running the Project

Install dependencies:

```id="8q1lgd"
pip install -r requirements.txt
```

Run the pipeline:

```id="p9oxk8"
python memory_sync.py
```

The script will ask for:

* a chat share link
* the source platform (chatgpt / claude / gemini)

After processing the conversation, memory packets and a project snapshot will be generated.

---

## Why I Built This

This project started as an experiment while working on several AI-assisted research projects.

I noticed that useful technical discussions were happening inside chat sessions, but there was no easy way to reuse that information later.

The goal here was not to build a full product, but to explore whether it is possible to create a lightweight memory layer that sits on top of AI tools.

---

## Possible Future Improvements

Some ideas that could be explored further:

* linking memory across multiple projects
* ranking or filtering important knowledge
* building a small UI for browsing stored context
* automatically injecting memory into prompts

---

## License

MIT License
