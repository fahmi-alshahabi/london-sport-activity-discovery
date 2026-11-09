"""C-14 security sanitisers (WP §12.8, §15.4).

AI-ASSISTED SCAFFOLD. NOT authorship evidence; a security/assurance reviewer must sign these, and
infrastructure controls (rate limits, headers, IAM, SBOM) are Wesley's (Section 16). Small, pure,
hand-checkable controls the applications must route exports/links/output through.
"""
from __future__ import annotations
import html as _html
from urllib.parse import urlparse

# Characters that trigger formula evaluation in spreadsheet apps (WP §15.4).
_FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def csv_field(value) -> str:
    """Neutralise spreadsheet formula injection by prefixing a single quote to risky values."""
    s = "" if value is None else str(value)
    if s and s[0] in _FORMULA_TRIGGERS:
        return "'" + s
    return s


def safe_url(url) -> str:
    """Return the URL only if it is an absolute http(s) URL; otherwise empty (blocks javascript:, data:, etc.)."""
    try:
        p = urlparse(str(url))
    except Exception:
        return ""
    return str(url) if p.scheme in ("http", "https") and p.netloc else ""


def escape_html(text) -> str:
    """Escape HTML special characters (defence in depth; templates already autoescape)."""
    return _html.escape("" if text is None else str(text), quote=True)
