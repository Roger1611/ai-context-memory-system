# Architecture Overview

This project is built as a small pipeline that processes AI conversations and extracts reusable project knowledge from them.

The system is intentionally simple. Each stage performs a specific task, and the output of one stage becomes the input for the next.

The main stages are:

* conversation ingestion
* conversation parsing
* memory extraction
* embedding and indexing
* context snapshot generation

---

## Conversation Ingestion

The first step is collecting the conversation itself.

A share link from an AI platform (for example ChatGPT) is provided, and the system fetches the page content and stores it locally.

The goal of this stage is simply to convert the conversation into a structured JSON format that can be processed later.

## Conversation Parsing

Once the conversation is stored, the parser analyzes the messages and extracts useful structural information.

This includes things like:

* referenced files
* folder structures mentioned in the chat
* commands that were executed
* imported Python modules

This stage helps identify developer-related artifacts that appear in technical discussions.

Module:

```id="pm8jha"
src/ingestion/conversation_parser.py
```

---

## Memory Extraction

After parsing, the system attempts to extract durable knowledge from the conversation.

A local LLM is used to identify information that may remain relevant beyond the specific chat session.

Examples include:

* architecture decisions
* research progress
* experimental results
* development workflows

The extracted information is stored as structured memory packets in JSON format.

Modules:

```id="z3gg8k"
src/extraction/memory_extractor.py
src/extraction/dev_memory_extractor.py
```

---

## Artifact Extraction

Technical discussions often contain useful artifacts such as repository structures or commands.

This component collects those elements so they can be stored separately from the general memory packets.

Module:

```id="mv0j0h"
src/extraction/artifact_extractor.py
```

---

## Embedding and Retrieval

To allow semantic search over stored knowledge, embeddings are generated for each memory packet.

These embeddings are stored in a FAISS index.

This makes it possible to retrieve relevant project knowledge even when the query wording is different from the original conversation.

---

## Context Snapshot Generation

The final step is generating a readable project snapshot.

This snapshot summarizes the most important information stored in the memory system, such as:

* current project progress
* important technical decisions
* repository structure
* possible next steps

The snapshot can be pasted into a new AI conversation to quickly restore project context.

---

## Design Approach

The system was designed with a few simple principles:

* keep the pipeline modular
* store knowledge in structured formats
* make the output usable across different AI tools

The implementation is intentionally lightweight so the system can be extended or modified easily.
