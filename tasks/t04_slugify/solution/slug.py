import re
import unicodedata


def slugify(text):
    """Convert arbitrary text into a URL slug (see task rules)."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if not text:
        return "untitled"
    if len(text) > 60:
        text = text[:60].rstrip("-")
    return text
