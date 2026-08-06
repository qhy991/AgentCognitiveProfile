"""Compiler — converts AST nodes into a callable that renders output."""

from parser import parse
from lexer import tokenize
from context import Context


def compile_template(nodes):
    """Compile a list of AST nodes into a render function.

    Returns a callable that takes a Context and returns a string.
    """
    def render(ctx):
        result = []
        for node in nodes:
            _render_node(node, ctx, result)
        return "".join(result)
    return render


def _render_node(node, ctx, result):
    """Render a single AST node into the result list."""
    from nodes import TextNode, VariableNode, BlockNode

    if isinstance(node, TextNode):
        result.append(node.text)

    elif isinstance(node, VariableNode):
        value = _eval_expression(node.expression, ctx)
        if ctx.auto_escape and isinstance(value, str):
            result.append(_escape_html(value))
        else:
            result.append(str(value))

    elif isinstance(node, BlockNode):
        if node.keyword == "if":
            _render_if(node, ctx, result)
        elif node.keyword == "for":
            _render_for(node, ctx, result)
        elif node.keyword == "include":
            _render_include(node, ctx, result)
        else:
            result.append(f"<!-- unknown block: {node.keyword} -->")


def _render_include(node, ctx, result):
    """Render an {% include %} block."""
    body = _tokens_to_text(node.body_tokens).strip().strip('"').strip("'")
    if ctx.loader:
        try:
            included = ctx.loader.load(body)
            sub_ctx = Context(
                variables=dict(ctx.variables),
                filters=dict(ctx.filters),
                loader=ctx.loader,
                auto_escape=ctx.auto_escape,
            )
            result.append(included._compiled(sub_ctx))
        except ValueError:
            result.append(f"<!-- template not found: {body} -->")
    else:
        result.append(f"<!-- include: {body} -->")


def _render_if(node, ctx, result):
    """Render an {% if %} block."""
    body_text = _tokens_to_text(node.body_tokens)
    parts = body_text.split("{% else %}", 1)
    condition = parts[0].strip()
    if _eval_condition(condition, ctx):
        result.append(parts[0])
    elif len(parts) > 1:
        result.append(parts[1])


def _render_for(node, ctx, result):
    """Render a {% for %} block."""
    body_text = _tokens_to_text(node.body_tokens)
    lines = body_text.split("\n", 1)
    header = lines[0].strip()
    body = lines[1] if len(lines) > 1 else ""
    parts = header.split(" in ", 1)
    if len(parts) != 2:
        return
    var_name = parts[0].strip()
    iter_name = parts[1].strip()
    items = ctx.variables.get(iter_name, [])
    for item in items:
        sub_ctx = ctx.push({var_name: item})
        sub_tokens = tokenize(body)
        sub_nodes = parse(sub_tokens)
        sub_render = compile_template(sub_nodes)
        result.append(sub_render(sub_ctx))


def _eval_expression(expr, ctx):
    """Evaluate a template expression like 'name' or 'name|upper'."""
    parts = expr.split("|")
    var_name = parts[0].strip()
    value = ctx.variables.get(var_name, "")
    for filter_name in parts[1:]:
        filter_name = filter_name.strip()
        if filter_name in ctx.filters:
            value = ctx.filters[filter_name](value)
    return value


def _eval_condition(condition, ctx):
    """Evaluate a simple condition."""
    cond = condition.strip()
    if cond.startswith("not "):
        var_name = cond[4:].strip()
        return not bool(ctx.variables.get(var_name))
    return bool(ctx.variables.get(cond))


def _tokens_to_text(tokens):
    """Convert raw tokens back to text."""
    return "".join(v for _, v in tokens)


def _escape_html(text):
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))