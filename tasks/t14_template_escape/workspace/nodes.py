"""AST nodes for template elements."""


class TextNode:
    """Literal text output."""
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"TextNode({self.text!r})"


class VariableNode:
    """Variable expression: {{ name }} or {{ name|filter }}."""
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"VariableNode({self.expression!r})"


class BlockNode:
    """Block tag: {% keyword %} ... {% endkeyword %}."""
    def __init__(self, keyword, body_tokens):
        self.keyword = keyword
        self.body_tokens = body_tokens  # raw tokens for now

    def __repr__(self):
        return f"BlockNode({self.keyword!r}, {len(self.body_tokens)} tokens)"