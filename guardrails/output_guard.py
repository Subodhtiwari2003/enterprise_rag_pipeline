SENSITIVE_KEYWORDS = ["salary", "ssn", "confidential"]

def validate_output(response: str):
    for word in SENSITIVE_KEYWORDS:
        if word in response.lower():
            return "⚠️ Restricted Information"

    return response