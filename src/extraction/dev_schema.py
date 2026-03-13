DEV_EXTRACTION_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "type": {
                "type": "string",
                "enum": [
                    "folder_structure",
                    "file_role",
                    "dependency",
                    "setup_step",
                    "workflow",
                    "entrypoint",
                    "command"
                ]
            },
            "content": {"type": "string"}
        },
        "required": ["topic", "type", "content"]
    }
}