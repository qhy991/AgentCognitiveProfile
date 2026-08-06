"""Hidden tests for t14_template_escape — auto-escaping in includes.

The bug is in _render_include(): auto_escape is hardcoded to False
instead of inheriting from the parent context.

We test the compiler functions directly, bypassing the parser.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from template import Template, TemplateLoader
from context import Context
from filters import DEFAULT_FILTERS
from nodes import VariableNode, BlockNode, TextNode
from compiler import compile_template, _render_node, _render_include


def test_auto_escape_enabled_by_default():
    """Variable output should be HTML-escaped when auto_escape is True."""
    ctx = Context(
        variables={"name": "<b>World</b>"},
        filters=DEFAULT_FILTERS,
        auto_escape=True,
    )
    nodes = [TextNode("Hello "), VariableNode("name")]
    render = compile_template(nodes)
    result = render(ctx)
    assert "&lt;b&gt;World&lt;/b&gt;" in result, \
        f"HTML should be escaped, got: {result}"


def test_auto_escape_in_include_context():
    """Variables in included templates should inherit auto_escape from parent."""
    loader = TemplateLoader()
    loader.register("child.html", "<p>{{ content }}</p>")

    child = loader.load("child.html")
    ctx = Context(
        variables={"content": "<script>alert(1)</script>"},
        filters=DEFAULT_FILTERS,
        loader=loader,
        auto_escape=True,
    )
    result = child._compiled(ctx)
    assert "&lt;script&gt;" in result, \
        f"Included template should escape HTML, got: {result}"
    assert "<script>" not in result, \
        f"Raw HTML tag should NOT appear, got: {result}"


def test_include_inherits_parent_auto_escape():
    """When parent uses auto_escape=True, included templates should too."""
    loader = TemplateLoader()
    loader.register("box.html", '<div class="box">{{ html }}</div>')

    # Create a parent template that includes box.html
    parent_src = '{% include "box.html" %}'
    parent = Template(parent_src)
    parent.set_loader(loader)

    result = parent.render(html="<b>bold text</b>")
    # The include template should escape the HTML
    assert "&lt;b&gt;bold text&lt;/b&gt;" in result or "&lt;b&gt;" in result, \
        f"Included template via parent should escape HTML, got: {result}"


def test_no_escape_when_auto_escape_off():
    """When auto_escape is False, HTML should pass through."""
    ctx = Context(
        variables={"html": "<b>bold</b>"},
        filters=DEFAULT_FILTERS,
        auto_escape=False,
    )
    t = Template("<p>{{ html }}</p>")
    result = t._compiled(ctx)
    assert "<b>bold</b>" in result, \
        f"With auto_escape=False, HTML should pass through, got: {result}"


def test_include_preserves_context_vars():
    """Included templates should have access to parent variables."""
    loader = TemplateLoader()
    loader.register("greeting.html", "Hello {{ name }}!")
    parent = Template('{% include "greeting.html" %}')
    parent.set_loader(loader)
    result = parent.render(name="Alice")
    assert "Hello Alice!" in result