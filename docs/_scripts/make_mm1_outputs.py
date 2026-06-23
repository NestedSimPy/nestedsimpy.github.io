"""Regenerate the Simple-example figure and dataset table from one nested run.

Both the illustration (``_static/mm1-nested-illustration.svg``) and the dataset
table embedded in ``simple-example.md`` are produced from a *single* nested
M/M/1 run that matches ``simpy_examples/mm1_nested.py`` exactly (seed 42,
lambda=3, mu=4, horizon 10, three inner branches per arrival).  Running this
keeps the figure, the table and the example code consistent.

The figure is drawn through the public :class:`nestedsimpy.OutputManager`, so it
doubles as a check that the API produces sensible output.

Usage (needs the nestedsimpy package on the path)::

    PYTHONPATH=/path/to/nestedsimpy-pkg python docs/_scripts/make_mm1_outputs.py

Outputs:
  * docs/_static/mm1-nested-illustration.svg      (overwritten)
  * docs/_static/mm1-dataset-table.html           (overwritten; <tbody> rows)
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nestedsimpy import NestedEnvironment, NestedResource, OutputManager
from nestedsimpy.reporting import package_run_outputs

# --- the exact configuration of simpy_examples/mm1_nested.py -----------------
ARRIVAL_RATE = 3.0
SERVICE_RATE = 4.0
SIM_TIME = 10.0
SEED = 42
BRANCHES = 3
INNER_HORIZON = 5.0

# Two triggering events to highlight in the illustration (chosen for a clear
# fan-out: one early, low-occupancy trigger and one near the busy peak).
HIGHLIGHT_TARGETS = (1.0, 3.5)
HIGHLIGHT_COLORS = ("#4c78c8", "#d6604d")  # blue, red -- matches the dots
# How far past each trigger to draw the inner branches. This matches the model's
# inner horizon (relative_time=5.0) so the picture agrees with the code and the
# caption ("each inner runs for 5 units of time").
INNER_SHOW = 5.0

DOCS = Path(__file__).resolve().parents[1]
STATIC = DOCS / "_static"
METRIC = "(srv)state_num_customers_in_system"


def run_model(out_dir: str) -> str:
    """Run the nested M/M/1 exactly as the example and return its run folder."""

    def customer(env, server):
        with server.request() as req:
            yield req
            yield env.nested_timeout(
                {"distribution": "exponential", "lambda": SERVICE_RATE}
            )

    def arrivals(env, server):
        while True:
            yield env.nested_timeout(
                {"distribution": "exponential", "lambda": ARRIVAL_RATE}
            )
            env.process(customer(env, server))

    env = NestedEnvironment()
    server = NestedResource(env, capacity=1, nested_id="srv")
    env.process(arrivals(env, server))
    env.set_output_options(out_dir=out_dir, gzip_trace=False)
    # Independent random streams per branch so the inner simulations explore
    # genuinely different futures (CRN would make them identical here).
    env.set_rng("independent")
    env.set_outer_seed(SEED)
    env.set_nested_triggering_objects(nested_id="srv")
    env.set_nesting_conditions({"on": "arrival", "frequency": 1})
    env.set_inner_repetitions(BRANCHES)
    env.set_inner_stopping_condition(relative_time=INNER_HORIZON)
    env.set_outer_stopping_condition(timeout=SIM_TIME)
    env.nested_run()

    for dirpath, _dirnames, _files in os.walk(out_dir):
        if os.path.basename(dirpath) == "raw":
            run_dir = os.path.dirname(dirpath)
            package_run_outputs(run_dir)
            return run_dir
    raise RuntimeError("no run directory produced")


def _series(rows, t_max=None):
    xs, ys = [], []
    for row in rows:
        value = row.get(METRIC)
        if value in (None, ""):
            continue
        t = float(row["t"])
        if t_max is not None and t > t_max:
            break
        xs.append(t)
        ys.append(float(value))
    return xs, ys


def build_figure(om: OutputManager, run_dir: str) -> None:
    """Outer trajectory (black) with a few triggers' inner branches overlaid."""

    triggers = om.triggers()
    # Choose the trigger nearest each target time.
    highlights = []
    for target, color in zip(HIGHLIGHT_TARGETS, HIGHLIGHT_COLORS):
        info = min(triggers, key=lambda t: abs((t.branch_time or 0.0) - target))
        highlights.append((info, color))

    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    ox, oy = _series(om.export_outer())
    ax.step(ox, oy, where="post", color="black", linewidth=1.8, label="Outer path", zorder=5)

    inner_label_used = False
    for info, color in highlights:
        bt_show = (info.branch_time or 0.0) + INNER_SHOW
        for k in info.inner_ids:
            rows = [r for r in om.export_inner(info.trigger_id, k) if r.get("segment") == "inner"]
            ix, iy = _series(rows, t_max=bt_show)
            ax.step(
                ix,
                iy,
                where="post",
                color=color,
                linewidth=0.9,
                alpha=0.4,
                zorder=3,
                label=None if inner_label_used else "Inner branches",
            )
            inner_label_used = True
        # trigger marker
        bt = info.branch_time or 0.0
        # value of the outer path at the trigger
        sys_at = next((y for x, y in zip(ox, oy) if x >= bt), oy[-1] if oy else 0)
        ax.axvline(bt, color=color, linewidth=0.8, linestyle=":", alpha=0.5, zorder=2)
        ax.scatter(
            [bt],
            [sys_at],
            color=color,
            s=70,
            zorder=6,
            label="Trigger point" if info is highlights[0][0] else None,
            edgecolor="white",
            linewidth=0.8,
        )

    ax.set_xlabel("Simulation time", fontsize=12)
    ax.set_ylabel("Number in system", fontsize=12)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    fig.tight_layout()
    out = STATIC / "mm1-nested-illustration.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def build_table(run_dir: str) -> None:
    """Emit the per-inner dataset table (<tbody> rows) for the example page."""

    exports = Path(run_dir) / "exports"
    pattern = re.compile(r"\]\[[0-9]+,[^]]+\]\[[0-9]+\]-metrics\.json$")
    records = []
    for path in exports.glob("*-metrics.json"):
        if not pattern.search(path.name) or "[all]" in path.name:
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        arrival = d["anchor_arrival_time"]
        start = d["service_start_time"]
        if start is None:  # started immediately on arrival (no wait)
            start = arrival
        wait = d["waiting_time"]
        if wait is None:
            wait = 0.0
        records.append(
            {
                "customer": int(d["anchor_cust_id"]),
                "branch": int(d["k"]) + 1,
                "arrival": arrival,
                "start": start,
                "end": d["service_end_time"],
                "wait": wait,
            }
        )
    records.sort(key=lambda r: (r["customer"], r["branch"]))

    def fmt(x):
        return "" if x is None else f"{x:.2f}"

    head = (
        '<div class="ns-dataset-scroll">\n'
        '<table class="ns-dataset-table">\n'
        "<thead><tr><th>Customer</th><th>Branch</th><th>Arrival</th>"
        "<th>Service start</th><th>Service end</th><th>Waiting time</th></tr></thead>\n"
        "<tbody>"
    )
    lines = [head]
    for r in records:
        lines.append(
            "<tr>"
            f"<td>{r['customer']}</td><td>{r['branch']}</td>"
            f"<td>{fmt(r['arrival'])}</td><td>{fmt(r['start'])}</td>"
            f"<td>{fmt(r['end'])}</td><td>{fmt(r['wait'])}</td>"
            "</tr>"
        )
    lines.append("</tbody>\n</table>\n</div>")
    table_html = "\n".join(lines)

    out = STATIC / "mm1-dataset-table.html"
    out.write_text(table_html + "\n", encoding="utf-8")
    print("wrote", out, f"({len(records)} rows)")

    # Inject the table into the {raw} html block of the Simple-example page so it
    # renders with its scroll wrapper (an {include} of raw HTML drops the table
    # tags). The markers live inside a ```{raw} html``` fence in simple-example.md.
    page = DOCS / "simple-example.md"
    text = page.read_text(encoding="utf-8")
    begin = "<!-- mm1-table:begin"
    end = "<!-- mm1-table:end -->"
    i = text.index(begin)
    i = text.index("-->", i) + len("-->")
    j = text.index(end)
    new_text = text[:i] + "\n" + table_html + "\n" + text[j:]
    page.write_text(new_text, encoding="utf-8")
    print("injected table into", page)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = run_model(os.path.join(tmp, "out"))
        om = OutputManager(run_dir)
        build_figure(om, run_dir)
        build_table(run_dir)


if __name__ == "__main__":
    main()
