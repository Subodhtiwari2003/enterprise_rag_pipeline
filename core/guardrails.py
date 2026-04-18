"""
Lightweight guardrail layer for enterprise safety.
Checks queries for PII, prompt injection, and off-topic content.
No heavy external packages required.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── PII Patterns ──────────────────────────────────────
PII_PATTERNS = {
    "aadhaar": r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b",
    "pan_card": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
    "email": r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    "phone_in": r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",
    "ssn": r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
}

# ── Prompt Injection Keywords ─────────────────────────
INJECTION_PATTERNS = [
    r"ignore (previous|all|above|prior) (instructions?|prompts?|context)",
    r"you are now",
    r"act as (a |an )?(different|new|another|evil|unrestricted)",
    r"forget (everything|all|your instructions)",
    r"jailbreak",
    r"DAN (mode|prompt)",
    r"disregard (your|all) (guidelines|rules|instructions)",
    r"bypass (safety|filters|restrictions)",
]

# ── Blocked Topics ────────────────────────────────────
BLOCKED_TOPICS = [
    r"\b(salary|ctc|compensation) of [A-Z][a-z]+ [A-Z][a-z]+",  # specific person salary
    r"\bpassword\b",
    r"\bpersonal (data|details) of\b",
    r"\bhack\b",
    r"\billegal\b",
]

# ── Valid Domains ─────────────────────────────────────
VALID_DOMAINS = {"hr", "finance"}


class GuardrailResult:
    def __init__(self, passed: bool, reason: str = ""):
        self.passed = passed
        self.reason = reason

    def __bool__(self):
        return self.passed


def check_pii(text: str) -> GuardrailResult:
    for label, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(False, f"PII detected: {label}")
    return GuardrailResult(True)


def check_injection(text: str) -> GuardrailResult:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(False, "Prompt injection attempt detected")
    return GuardrailResult(True)


def check_blocked_topics(text: str) -> GuardrailResult:
    for pattern in BLOCKED_TOPICS:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(False, "Query contains restricted topic")
    return GuardrailResult(True)


def check_query_length(text: str, max_chars: int = 1000) -> GuardrailResult:
    if len(text.strip()) < 5:
        return GuardrailResult(False, "Query is too short")
    if len(text) > max_chars:
        return GuardrailResult(False, f"Query exceeds maximum length of {max_chars} characters")
    return GuardrailResult(True)


def check_domain(domain: str) -> GuardrailResult:
    if domain.lower() not in VALID_DOMAINS:
        return GuardrailResult(False, f"Invalid domain '{domain}'. Valid: {sorted(VALID_DOMAINS)}")
    return GuardrailResult(True)


def run_input_guardrails(query: str, domain: str) -> GuardrailResult:
    """Run all input guardrail checks. Returns first failure or pass."""
    checks = [
        check_query_length(query),
        check_domain(domain),
        check_pii(query),
        check_injection(query),
        check_blocked_topics(query),
    ]
    for result in checks:
        if not result.passed:
            logger.warning(f"Guardrail blocked query | Reason: {result.reason} | Query: {query[:80]}")
            return result
    return GuardrailResult(True, "All checks passed")


def run_output_guardrails(response: str) -> GuardrailResult:
    """Check LLM output for PII leakage before returning to user."""
    pii_check = check_pii(response)
    if not pii_check.passed:
        logger.warning(f"PII detected in LLM output — response suppressed")
        return GuardrailResult(False, "Response contained sensitive information and was blocked")
    return GuardrailResult(True, "Output check passed")