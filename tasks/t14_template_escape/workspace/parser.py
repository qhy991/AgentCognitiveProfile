"""Parser — converts token stream into an AST of template nodes."""

from nodes import TextNode, VariableNode, BlockNode


def parse(tokens):
    """Parse tokens into a list of AST nodes.

    Simplified grammar:
        template = (text | variable | block)*
        variable = "{{" expression "}}"
        block    = "{%" keyword expression "%}" ... "{%" "end" keyword "%}"
    """
    nodes = []
    pos = 0

    while pos < len(tokens):
        kind, value = tokens[pos]

        if kind == "TEXT":
            nodes.append(TextNode(value))
            pos += 1

        elif kind == "VAR_START":
            pos += 1  # skip {{
            expr = ""
            while pos < len(tokens) and tokens[pos][0] != "VAR_END":
                _, v = tokens[pos]
                expr += v
                pos += 1
            pos += 1  # skip }}
            nodes.append(VariableNode(expr.strip()))

        elif kind == "BLOCK_START":
            pos += 1  # skip {%
            # Get the block keyword and arguments
            block_text = ""
            while pos < len(tokens) and tokens[pos][0] == "TEXT":
                _, v = tokens[pos]
                block_text += v
                pos += 1
            block_text = block_text.strip()
            # Split into keyword and rest
            parts = block_text.split(None, 1)
            keyword = parts[0] if parts else ""
            rest = parts[1] if len(parts) > 1 else ""

            # Parse block content until {% endkeyword %} or %}
            body_tokens = []
            # If there's remaining text, add it as body tokens
            if rest:
                body_tokens.append(("TEXT", rest))
            depth = 1
            while pos < len(tokens) and depth > 0:
                tk, tv = tokens[pos]
                if tk == "BLOCK_END":
                    # Self-closing block like {% include "x" %}
                    pos += 1
                    break
                if tk == "BLOCK_START":
                    # Check if it's an end tag
                    lookahead = pos + 1
                    while lookahead < len(tokens) and tokens[lookahead][0] == "TEXT":
                        inner = tokens[lookahead][1].strip()
                        if inner.startswith("end"):
                            depth -= 1
                            if depth == 0:
                                pos = lookahead + 1  # skip past end tag
                                # skip to BLOCK_END
                                while pos < len(tokens) and tokens[pos][0] != "BLOCK_END":
                                    pos += 1
                                pos += 1  # skip %}
                                break
                        break
                    else:
                        depth += 1
                        body_tokens.append((tk, tv))
                        pos += 1
                        continue
                    if depth == 0:
                        break
                body_tokens.append((tk, tv))
                pos += 1

            nodes.append(BlockNode(keyword, body_tokens))

        else:
            pos += 1  # skip unexpected tokens

    return nodes