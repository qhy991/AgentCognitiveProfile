"""String buffer for building large text outputs.

Provides efficient string building for report generation,
log formatting, and other text-heavy operations.
"""


class StringBuffer:
    """A mutable string buffer for building text incrementally.

    Supports append, prepend, and insert operations.
    Used heavily in our report generation pipeline.
    """

    def __init__(self):
        self._lines = []

    def append(self, text):
        """Add text to the end of the buffer."""
        self._lines.append(text)

    def prepend(self, text):
        """Add text to the beginning of the buffer.

        BUG: Uses list.insert(0, ...) which is O(n) per call.
        Building a buffer with N prepends is O(n²).
        """
        self._lines.insert(0, text)

    def extend(self, texts):
        """Add multiple lines to the end."""
        self._lines.extend(texts)

    def build(self):
        """Return the complete buffer contents as a string."""
        return "\n".join(self._lines)

    def clear(self):
        """Clear the buffer."""
        self._lines.clear()

    def __len__(self):
        return len(self._lines)

    def __str__(self):
        return self.build()


class ReportBuilder:
    """Builds a structured report with header, body, and footer.

    Uses StringBuffer internally.
    """

    def __init__(self, title=""):
        self._buffer = StringBuffer()
        if title:
            self._buffer.append(f"# {title}")
            self._buffer.append("")

    def add_header(self, text, level=2):
        """Add a section header."""
        prefix = "#" * level
        self._buffer.append(f"{prefix} {text}")
        self._buffer.append("")

    def add_line(self, text):
        """Add a line of text."""
        self._buffer.append(text)

    def add_table(self, headers, rows):
        """Add a markdown table."""
        self._buffer.append("| " + " | ".join(headers) + " |")
        self._buffer.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in rows:
            self._buffer.append("| " + " | ".join(str(c) for c in row) + " |")
        self._buffer.append("")

    def add_footer(self, text):
        """Add a footer line."""
        self._buffer.append("")
        self._buffer.append("---")
        self._buffer.append(text)

    def prepend_toc(self, entries):
        """Prepend a table of contents (inserted at the beginning).

        BUG: Each prepend is O(n), making this O(n²) for many entries.
        """
        self._buffer.prepend("")
        self._buffer.prepend("## Table of Contents")
        for entry in reversed(entries):
            self._buffer.prepend(f"- [{entry}](#{entry.lower().replace(' ', '-')})")

    def build(self):
        """Return the complete report."""
        return self._buffer.build()