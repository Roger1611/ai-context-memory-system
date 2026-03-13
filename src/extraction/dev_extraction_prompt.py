DEV_EXTRACTION_PROMPT = """
You are extracting developer knowledge from a conversation where a developer and an AI assistant built a software system.

Your task is to extract information that another developer would need to understand, run, or continue the project.

Focus ONLY on durable developer knowledge.

Extract the following categories:

1. Repository structure
   - folders
   - files
   - package layout

2. File responsibilities
   - what each file does
   - module purpose
   - code responsibilities

3. Execution flow
   - entrypoints
   - main pipeline scripts
   - system workflow

4. Dependencies
   - libraries
   - tools
   - frameworks
   - models

5. Commands
   - setup commands
   - run commands
   - test commands

IMPORTANT RULES:

- Preserve folder trees exactly if they appear.
- Preserve file paths exactly.
- Preserve commands exactly.
- Ignore reasoning explanations.
- Ignore discussion that is not developer-operational knowledge.

Return JSON in this format:

[
  {
    "topic": "...",
    "type": "...",
    "content": "..."
  }
]

Allowed types:

folder_structure
file_role
dependency
setup_step
workflow
entrypoint
command
"""