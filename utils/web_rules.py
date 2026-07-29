import re

# attack pattern rules
RULES = {
    "SQL Injection": [
        r"(?i)(\bor\b|\band\b)\s+[\w'\"]+\s*=\s*[\w'\"]+",
        r"(?i)(union\s+select|select\s+.*\s+from|insert\s+into|drop\s+table|--\s*$|;\s*--)",
        r"(?i)('\s*(or|and)\s*'?\d)",
        r"(?i)(sleep\s*\(|benchmark\s*\(|waitfor\s+delay)",
        r"(?i)(xp_cmdshell|exec\s*\(|execute\s*\()",
    ],
    "XSS": [
        r"(?i)<\s*script.*?>",
        r"(?i)javascript\s*:",
        r"(?i)on\w+\s*=\s*['\"].*?['\"]",
        r"(?i)<\s*img.*?onerror",
        r"(?i)eval\s*\(",
    ],
    "Path Traversal": [
        r"(\.\./|\.\.\\){2,}",
        r"(?i)(etc/passwd|etc/shadow|win\.ini|boot\.ini)",
    ],
    "Command Injection": [
        r"(?i)(\||;|`|&&|\$\()\s*(ls|cat|whoami|id|uname|wget|curl|bash|sh)\b",
    ],
}

def check_web_rules(url: str = "", payload: str = "", headers: dict = None) -> dict:
    """
    Run rule-based checks on url, payload, and headers.
    Returns { matched: bool, attack_type: str, matched_rule: str }
    """
    targets = [url or "", payload or ""]
    if headers:
        targets += list(headers.values())

    combined = " ".join(str(t) for t in targets)

    for attack_type, patterns in RULES.items():
        for pattern in patterns:
            if re.search(pattern, combined):
                return {
                    "matched": True,
                    "attack_type": attack_type,
                    "matched_rule": pattern
                }

    return {"matched": False, "attack_type": None, "matched_rule": None}
