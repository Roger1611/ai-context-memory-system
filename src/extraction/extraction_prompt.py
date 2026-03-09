def build_extraction_prompt(conversation_text):

    prompt = f"""
You are an AI system that extracts durable project knowledge.

Your job is to read a conversation and extract only information
that represents lasting knowledge about a project.

Ignore greetings, filler text, and casual conversation.

Extract:

- experiment results
- design decisions
- architecture details
- constraints
- important insights

Return ONLY JSON in this format:

[
  {{
    "topic": "...",
    "type": "...",
    "content": "..."
  }}
]

Conversation:

{conversation_text}

JSON:
"""

    return prompt