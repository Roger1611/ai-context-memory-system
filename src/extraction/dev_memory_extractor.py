import json
import ast
from src.llm.ollama_client import generate_response
from src.extraction.dev_extraction_prompt import DEV_EXTRACTION_PROMPT


def extract_dev_knowledge(conversation_text):

    prompt = f"""
{DEV_EXTRACTION_PROMPT}

Conversation:

{conversation_text}
"""

    response = generate_response(prompt)

    if isinstance(response, list):
        return response

    if isinstance(response, str):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

    try:
        return ast.literal_eval(response)
    except Exception:
        print("[WARN] Developer extraction parsing failed")
        return []