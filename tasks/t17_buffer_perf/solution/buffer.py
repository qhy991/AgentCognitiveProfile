"""String buffer for building large text outputs.

Provides efficient string building for report generation,
log formatting, and other text-heavy operations.
"""


class StringBuffer:
    """A mutable string buffer for building text incrementally."""

    def __init__(self):
        self._lines = []
        self._prepends = []  # Collect prepends separately

    def append(self, text):
        """Add text to the end of the buffer."""
        self._lines.append(text)

    def prepend(self, text):
        """Add text to the beginning of the buffer.

        Uses a separate list for prepends to avoid O(n) insert.
        Prepends are applied in reverse order at build time.
        """
        self._prepends.append(text)

    def extend(self, texts):
        """Add multiple lines to the end."""
        self._lines.extend(texts)

    def build(self):
        """Return the complete buffer contents."""
        all_lines = list(reversed(self._prepends)) + self._lines
        return "\n".join(all_lines)

    def clear(self):
        """Clear the buffer."""
        self._lines.clear()
        self._prepends.clear()

    def __len__(self):
        return len(self._lines) + len(self._prepends)

    def __str__(self):
        return self.build()


class ReportBuilder:
    """Builds a structured report with header, body, and footer."""

    def __init__(self, title=""):
        self._buffer = StringBuffer()
        if title:
            self._buffer.append(f"# {title}")
            self._buffer.append("")

    def add_header(self, text, level=2):
        prefix = "#" * level
        self._buffer.append(f"{prefix} {text}")
        self._buffer.append("")

    def add_line(self, text):
        self._buffer.append(text)

    def add_table(self, headers, rows):
        self._buffer.append("| " + " | ".join(headers) + " |")
        self._buffer.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in rows:
            self._buffer.append("| " + " | ".join(str(c) for c in row) + " |")
        self._buffer.append("")

    def add_footer(self, text):
        self._buffer.append("")
        self._buffer.append("---")
        self._buffer.append(text)

    def prepend_toc(self, entries):
        self._buffer.prepend("")
        self._buffer.prepend("## Table of Contents")
        for entry in reversed(entries):
            self._buffer.prepend(f"- [{entry}](#{entry.lower().replace(' ', '-')})")

    def build(self):
        return self._buffer.build()