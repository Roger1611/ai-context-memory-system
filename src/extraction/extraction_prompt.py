def build_extraction_prompt(conversation_text):

    return f"""
You are a system that extracts structured project knowledge from AI conversations.

Your task is to identify important project information and return it in JSON format.

IMPORTANT RULES:
- Output ONLY JSON.
- Do NOT include explanations.
- Do NOT include text before or after the JSON.
- The JSON must be a list of objects.

Each object must have:

topic
type
content

Example:

[
  {{
    "topic": "architecture",
    "type": "system_design",
    "content": "The system uses Playwright to ingest share links and FAISS for semantic retrieval."
  }},
  {{
    "topic": "current_progress",
    "type": "project_state",
    "content": "Conversation ingestion and memory extraction modules are implemented."
  }}
]

Extract information about:

- project goal
- problem statement
- system architecture
- repository structure
- completed components
- current progress
- important technical decisions
- algorithms used
- datasets used
- experiments performed
- code modules or files implemented
- open questions
- next steps
- limitations

Only include information that appears in the conversation.

Conversation starts below.

-----BEGIN CONVERSATION-----

{conversation_text}

-----END CONVERSATION-----

Return JSON only.
"""