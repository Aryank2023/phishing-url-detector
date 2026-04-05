from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any
from urllib.parse import urlparse

SUSPICIOUS_WORDS = (
    "account",
    "bank",
    "billing",
    "confirm",
    "login",
    "password",
    "pay",
    "secure",
    "signin",
    "update",
    "verify",
    "wallet",
    "webscr",
)

SHORTENER_DOMAINS = {
    "bit.ly",
    "cutt.ly",
    "goo.gl",
    "is.gd",
    "ow.ly",
    "rb.gy",
    "rebrand.ly",
    "shorturl.at",
    "t.co",
    "tinyurl.com",
}

IPV4_PATTERN = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def normalize_url(raw_url: str) -> str:
    candidate = (raw_url or "").strip()
    if not candidate:
        return ""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", candidate):
        candidate = f"https://{candidate}"
    return candidate


def is_probably_valid_url(raw_url: str) -> bool:
    normalized = normalize_url(raw_url)
    if not normalized:
        return False
    parsed = urlparse(normalized)
    return bool(parsed.scheme and parsed.netloc and "." in parsed.netloc)


def _safe_ratio(part: int, whole: int) -> float:
    return round(part / whole, 4) if whole else 0.0


def extract_url_features(raw_url: str) -> dict[str, Any]:
    normalized = normalize_url(raw_url)
    parsed = urlparse(normalized)
    hostname = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()
    query = (parsed.query or "").lower()
    full_text = normalized.lower()

    special_counts = Counter(char for char in normalized if not char.isalnum())
    digits = sum(char.isdigit() for char in normalized)
    letters = sum(char.isalpha() for char in normalized)
    subdomain_count = max(hostname.count(".") - 1, 0) if hostname else 0
    hyphen_count = hostname.count("-")
    suspicious_hits = sum(word in full_text for word in SUSPICIOUS_WORDS)
    tld = hostname.split(".")[-1] if "." in hostname else hostname

    return {
        "url_length": len(normalized),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "digit_count": digits,
        "digit_ratio": _safe_ratio(digits, len(normalized)),
        "letter_ratio": _safe_ratio(letters, len(normalized)),
        "dot_count": normalized.count("."),
        "slash_count": normalized.count("/"),
        "question_count": normalized.count("?"),
        "equal_count": normalized.count("="),
        "ampersand_count": normalized.count("&"),
        "percent_count": normalized.count("%"),
        "hyphen_count": hyphen_count,
        "underscore_count": normalized.count("_"),
        "at_symbol": int("@" in normalized),
        "double_slash_path": int("//" in normalized.split("://", 1)[-1]),
        "has_https": int(parsed.scheme == "https"),
        "subdomain_count": subdomain_count,
        "uses_ip_address": int(bool(IPV4_PATTERN.match(hostname))),
        "is_shortener": int(hostname in SHORTENER_DOMAINS),
        "suspicious_word_count": suspicious_hits,
        "has_login": int("login" in full_text),
        "has_verify": int("verify" in full_text),
        "has_account": int("account" in full_text),
        "has_secure": int("secure" in full_text),
        "has_update": int("update" in full_text),
        "has_bank": int("bank" in full_text),
        "entropy_hint": round(_shannon_entropy(normalized), 4),
        "special_char_density": _safe_ratio(sum(special_counts.values()), len(normalized)),
        "tld": tld or "unknown",
    }


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())
