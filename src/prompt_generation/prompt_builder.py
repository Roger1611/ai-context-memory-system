class PromptBuilder:
    def build_prompt(self, query, memory_packets):
        context_lines = []
        for i, packet in enumerate(memory_packets, start=1):
            line = f"{i}. ({packet['topic']}) {packet['content']}"
            context_lines.append(line)
        context_text = "\n".join(context_lines)
        prompt = f"""
You are an AI assistant helping with a software project.

Below is the relevant project context extracted from past AI conversations.

Project Context:
{context_text}

User Question:
{query}

Using the project context above, answer the user's question.
If the context is insufficient, explain what information is missing.
"""

        return prompt.strip()