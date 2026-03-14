from src.llm.ollama_client import generate_response
from src.extraction.dev_extraction_prompt import DEV_EXTRACTION_PROMPT
from src.config import DEV_MODEL

def extract_dev_knowledge(conversation_text, conversation_id):
    prompt = f"{DEV_EXTRACTION_PROMPT}\n{conversation_text}"
    print("[INFO] Sending conversation to Dev LLM for detailed explanation...")
    response = generate_response(prompt, DEV_MODEL)
    
    if not response.strip(): return []
    return [{
        "project": "ai_context",
        "topic": "developer_explanation",
        "type": "dev_summary",
        "content": response.strip(),
        "source_conversation": conversation_id,
        "source": "dev_extraction"
    }]