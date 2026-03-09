# AI Context Memory System

Cross-LLM memory layer that extracts durable knowledge from AI conversations
and generates portable context packets for any LLM.

## Architecture

Share Link → Conversation Parser → Memory Extraction → Memory Packets → Retrieval

## Structure

src/
    ingestion/
    extraction/
    llm/
    utils/

scripts/
    run_ingestion.py
    run_extraction.py