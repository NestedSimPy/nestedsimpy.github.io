"""Sphinx directives for showing how a nested adaptation differs from a plain
SimPy baseline.

Two directives are provided:

``codediff`` — Beyond-Compare-style two-pane diff of two source files::

    ```{codediff} ../../simpy_examples/foo_plain.py ../../simpy_examples/foo_nested.py
    :left-title: foo_plain.py
    :right-title: foo_nested.py
    :context: 3
    ```

``codeannotate`` — single-column, full-width view of the NESTED file with new
lines tinted green and modified lines tinted amber relative to the plain
baseline. Because there is no narrow second column, lines never wrap, so it
stays readable on long files::

    ```{codeannotate} ../../simpy_examples/foo_plain.py ../../simpy_examples/foo_nested.py
    :title: foo_nested.py
    :context: 3
    ```

Both reuse the theme's Pygments classes, so light/dark mode both work, and both
fold long unchanged runs behind a "show N unchanged lines" expander when
``:context:`` is given (wired up in custom.js).
"""
from __future__ import annotations

import difflib
import html
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import directives
from pygments.lexers import get_lexer_for_filename
from pygments.token import STANDARD_TYPES
from pygments.util import ClassNotFound
from sphinx.util.docutils import SphinxDirective


def _css_class(ttype):
    while ttype not in STANDARD_TYPES:
        ttype = ttype.parent
    return STANDARD_TYPES[ttype]


def _highlight_lines(code: str, filename: str) -> list[str]:
    """Highlight a whole file, then split into per-line HTML.

    Tokens are split on newlines before rendering, so multi-line tokens
    (docstrings) stay correctly highlighted on every line.
    """
    raw_count = len(code.splitlines())
    try:
        lexer = get_lexer_for_filename(filename, code)
    except ClassNotFound:
        return [html.escape(line) for line in code.splitlines()]
    lines: list[list[str]] = [[]]
    for ttype, value in lexer.get_tokens(code):
        for i, part in enumerate(value.split("\n")):
            if i:
                lines.append([])
            if part:
                cls = _css_class(ttype)
                esc = html.escape(part)
                lines[-1].append(f'<span class="{cls}">{esc}</span>' if cls else esc)
    rendered = ["".join(parts) for parts in lines]
    # get_tokens() guarantees a trailing newline, which adds one empty line.
    return rendered[:raw_count]


def _diff_rows(left_raw: list[str], right_raw: list[str]):
    """Yield (kind, left_index, right_index) rows; indexes are 0-based or None."""
    sm = difflib.SequenceMatcher(a=left_raw, b=right_raw, autojunk=False)
    rows = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            rows.extend(("eq", i1 + k, j1 + k) for k in range(i2 - i1))
        elif tag == "delete":
            rows.extend(("del", i, None) for i in range(i1, i2))
        elif tag == "insert":
            rows.extend(("ins", None, j) for j in range(j1, j2))
        else:  # replace: pair lines positionally, overflow becomes pure ins/del
            for k in range(max(i2 - i1, j2 - j1)):
                li = i1 + k if i1 + k < i2 else None
                rj = j1 + k if j1 + k < j2 else None
                kind = "chg" if li is not None and rj is not None else ("del" if li is not None else "ins")
                rows.append((kind, li, rj))
    return rows


class CodeDiff(SphinxDirective):
    required_arguments = 2
    option_spec = {
        "left-title": directives.unchanged,
        "right-title": directives.unchanged,
        "context": directives.nonnegative_int,
    }

    _fold_counter = 0

    def run(self):
        rel_left, abs_left = self.env.relfn2path(self.arguments[0])
        rel_right, abs_right = self.env.relfn2path(self.arguments[1])
        self.env.note_dependency(rel_left)
        self.env.note_dependency(rel_right)

        left_code = Path(abs_left).read_text(encoding="utf-8")
        right_code = Path(abs_right).read_text(encoding="utf-8")
        left_raw = left_code.splitlines()
        right_raw = right_code.splitlines()
        left_html = _highlight_lines(left_code, abs_left)
        right_html = _highlight_lines(right_code, abs_right)

        rows = _diff_rows(left_raw, right_raw)
        context = self.options.get("context")

        n_ins = sum(1 for k, _, _ in rows if k == "ins")
        n_del = sum(1 for k, _, _ in rows if k == "del")
        n_chg = sum(1 for k, _, _ in rows if k == "chg")

        left_title = self.options.get("left-title", Path(abs_left).name)
        right_title = self.options.get("right-title", Path(abs_right).name)

        body: list[str] = []

        def emit(kind, li, rj, hidden_group=None):
            ln_l = str(li + 1) if li is not None else ""
            ln_r = str(rj + 1) if rj is not None else ""
            src_l = left_html[li] if li is not None else ""
            src_r = right_html[rj] if rj is not None else ""
            cls = f"cd-{kind}"
            attrs = ""
            if hidden_group is not None:
                cls += " cd-hidden"
                attrs = f' data-fold="{hidden_group}"'
            body.append(
                f'<tr class="{cls}"{attrs}>'
                f'<td class="cd-ln">{ln_l}</td><td class="cd-src">{src_l}</td>'
                f'<td class="cd-ln">{ln_r}</td><td class="cd-src">{src_r}</td></tr>'
            )

        i = 0
        while i < len(rows):
            kind = rows[i][0]
            if kind != "eq" or context is None:
                emit(*rows[i])
                i += 1
                continue
            # run of equal rows
            j = i
            while j < len(rows) and rows[j][0] == "eq":
                j += 1
            run = rows[i:j]
            head = context if i > 0 else 0  # no leading context at file start
            tail = context if j < len(rows) else 0  # none at file end
            if len(run) > head + tail + 3:
                CodeDiff._fold_counter += 1
                gid = f"cdf{CodeDiff._fold_counter}"
                for r in run[:head]:
                    emit(*r)
                hidden = run[head:len(run) - tail if tail else len(run)]
                body.append(
                    f'<tr class="cd-expander" data-foldid="{gid}"><td colspan="4">'
                    f'<button type="button" class="cd-expand">&#8943; show {len(hidden)} '
                    f"unchanged lines &#8943;</button></td></tr>"
                )
                for r in hidden:
                    emit(*r, hidden_group=gid)
                if tail:
                    for r in run[len(run) - tail:]:
                        emit(*r)
            else:
                for r in run:
                    emit(*r)
            i = j

        out = (
            '<div class="ns-codediff">'
            '<div class="ns-cd-head">'
            f'<span class="ns-cd-title">{html.escape(left_title)}</span>'
            '<span class="ns-cd-stats">'
            f'<span class="cd-stat-del">&minus;{n_del}</span>'
            f'<span class="cd-stat-chg">~{n_chg}</span>'
            f'<span class="cd-stat-ins">+{n_ins}</span>'
            "</span>"
            f'<span class="ns-cd-title">{html.escape(right_title)}</span>'
            "</div>"
            '<div class="ns-cd-scroll"><table class="ns-cd-table highlight">'
            '<colgroup><col class="cd-col-ln"/><col class="cd-col-src"/>'
            '<col class="cd-col-ln"/><col class="cd-col-src"/></colgroup>'
            + "".join(body)
            + "</table></div></div>"
        )
        return [nodes.raw("", out, format="html")]


class CodeAnnotate(SphinxDirective):
    """Single-column, full-width view of the NESTED (second) file.

    Each line that exists in the nested file is shown in order, syntax
    highlighted, and tinted by how it differs from the plain (first) baseline:
    a line that is new in the nested file is tinted green; a line that is a
    modified version of a plain line is tinted amber. Lines that exist only in
    the plain file are simply absent (they are not part of the nested code).

    Unlike ``codediff`` there is no second column, so source lines use the full
    content width and never wrap into a narrow gutter.
    """

    required_arguments = 2  # plain (baseline), nested (shown)
    option_spec = {
        "title": directives.unchanged,
        "context": directives.nonnegative_int,
    }

    _fold_counter = 0

    def run(self):
        rel_left, abs_left = self.env.relfn2path(self.arguments[0])
        rel_right, abs_right = self.env.relfn2path(self.arguments[1])
        self.env.note_dependency(rel_left)
        self.env.note_dependency(rel_right)

        left_raw = Path(abs_left).read_text(encoding="utf-8").splitlines()
        right_code = Path(abs_right).read_text(encoding="utf-8")
        right_raw = right_code.splitlines()
        right_html = _highlight_lines(right_code, abs_right)

        rows = _diff_rows(left_raw, right_raw)
        # Keep only lines that exist in the nested file (drop plain-only deletes).
        nested = [(kind, rj) for (kind, _li, rj) in rows if rj is not None]

        n_ins = sum(1 for k, _ in nested if k == "ins")
        n_chg = sum(1 for k, _ in nested if k == "chg")
        context = self.options.get("context")
        title = self.options.get("title", Path(abs_right).name)

        body: list[str] = []

        def emit(kind, rj, hidden_group=None):
            ln = str(rj + 1)
            src = right_html[rj]
            cls = f"ca-{kind}"
            attrs = ""
            if hidden_group is not None:
                cls += " cd-hidden"
                attrs = f' data-fold="{hidden_group}"'
            body.append(
                f'<tr class="{cls}"{attrs}>'
                f'<td class="ca-ln">{ln}</td><td class="ca-src">{src}</td></tr>'
            )

        i = 0
        while i < len(nested):
            kind = nested[i][0]
            if kind != "eq" or context is None:
                emit(*nested[i])
                i += 1
                continue
            # run of unchanged lines
            j = i
            while j < len(nested) and nested[j][0] == "eq":
                j += 1
            run = nested[i:j]
            head = context if i > 0 else 0      # no leading context at file start
            tail = context if j < len(nested) else 0  # none at file end
            if len(run) > head + tail + 3:
                CodeAnnotate._fold_counter += 1
                gid = f"caf{CodeAnnotate._fold_counter}"
                for r in run[:head]:
                    emit(*r)
                hidden = run[head:len(run) - tail if tail else len(run)]
                body.append(
                    f'<tr class="cd-expander" data-foldid="{gid}"><td colspan="2">'
                    f'<button type="button" class="cd-expand">&#8943; show {len(hidden)} '
                    f"unchanged lines &#8943;</button></td></tr>"
                )
                for r in hidden:
                    emit(*r, hidden_group=gid)
                if tail:
                    for r in run[len(run) - tail:]:
                        emit(*r)
            else:
                for r in run:
                    emit(*r)
            i = j

        out = (
            '<div class="ns-codeannot">'
            '<div class="ns-ca-head">'
            f'<span class="ns-ca-title">{html.escape(title)}</span>'
            '<span class="ns-ca-legend">'
            '<span class="ca-key ca-key-ins">new</span>'
            '<span class="ca-key ca-key-chg">changed</span>'
            "</span>"
            '<span class="ns-ca-stats">'
            f'<span class="cd-stat-chg">~{n_chg}</span>'
            f'<span class="cd-stat-ins">+{n_ins}</span>'
            "</span>"
            "</div>"
            '<div class="ns-ca-scroll"><table class="ns-ca-table highlight">'
            '<colgroup><col class="ca-col-ln"/><col class="ca-col-src"/></colgroup>'
            + "".join(body)
            + "</table></div></div>"
        )
        return [nodes.raw("", out, format="html")]


def setup(app):
    app.add_directive("codediff", CodeDiff)
    app.add_directive("codeannotate", CodeAnnotate)
    return {"version": "0.2", "parallel_read_safe": True, "parallel_write_safe": True}
