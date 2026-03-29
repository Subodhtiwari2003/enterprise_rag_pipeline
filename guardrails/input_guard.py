import re

BLOCK_PATTERNS = [
    r"ignore previous instructions",
    r"bypass security",
    r"system prompt",
]

def validate_input(query: str):
    for pattern in BLOCK_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError("Prompt Injection Detected")

    return query