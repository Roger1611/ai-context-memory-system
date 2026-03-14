DEV_EXTRACTION_PROMPT = """TASK: Write a Developer Handoff Document.
Analyze this chat and explain every detail that would help another developer continue from the exact left-off point.

DO NOT OUTPUT A JSON ARRAY. Write a highly detailed Markdown document.

Include these exact sections:
### Dependencies & Setup Instructions
### File Responsibilities & Logic
### Workflow & System Execution
### Known Issues & Developer Notes

Conversation:
"""