Stage 1: Conversation Ingestion

User provides an AI share link.

System pipeline:

-Share Link

-Playwright Headless Browser

-Rendered HTML

-Conversation Parser

-Structured Messages

-JSON Storage

Output format:

{
  conversation_id
  source
  share_link
  timestamp
  messages[]
}

Future stages will consume these stored conversations
for memory extraction and semantic indexing.