# PyNestedSim Documentation

Public documentation site for **PyNestedSim** — a SimPy-based toolkit for
nested ("branch-after") discrete-event simulation.

> This repository contains the **documentation only**. The implementation
> package source is maintained privately. The API reference here is
> hand-written from the public interface and the build does **not** import or
> render any package source code.

## Build locally

```bash
pip install -r docs/requirements.txt
python -m sphinx -b html docs docs/_build/html
# open docs/_build/html/index.html
```

## Deployment

Pushes to `main` build and publish to GitHub Pages via
`.github/workflows/docs.yml` (no package source required to build).

## Layout

- `docs/` — Sphinx sources (MyST Markdown + hand-written API reference)
- `simpy_examples/` — usage example scripts embedded by the official-parity pages
