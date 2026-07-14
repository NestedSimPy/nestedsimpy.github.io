"""Regenerate the Simple-example figures and tables from one nested run.

The four figures (static outer, interactive outer, one inner, all inners) and the
three dataset tables (one inner path, the outer path, the prediction table) on
``simple-example.md`` are all produced from a single nested M/M/1 run that
matches ``simpy_examples/mm1_nested.py`` (seed 42, independent branches). The
plotted metric is the **queue length** at the server.

Usage (needs the nestedsimpy package on the path)::

    PYTHONPATH=/path/to/nestedsimpy-pkg python docs/_scripts/make_mm1_outputs.py

Outputs (overwritten) under docs/_static/:
  mm1-outer-static.svg, mm1-interactive.html, mm1-inner-one.svg, mm1-inner-all.svg
  mm1-table-inner.html, mm1-table-outer.html, mm1-table-pred.html
and the three tables are injected into simple-example.md between their markers.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nestedsimpy import NestedEnvironment, NestedResource, OutputManager
from nestedsimpy.reporting import package_run_outputs, write_dynamic_plot

# --- the exact configuration of simpy_examples/mm1_nested.py -----------------
ARRIVAL_RATE = 3.0
SERVICE_RATE = 4.0
SIM_TIME = 10.0
SEED = 42
BRANCHES = 3
INNER_HORIZON = 5.0

# Queue length at the server is the plotted metric.
QUEUE_FIELD = "state_num_customers_in_queue"
METRIC = "(srv)" + QUEUE_FIELD
Y_LABEL = "Queue length (srv)"

# The three per-resource state columns of the server, as (CSV column, header).
STATE_COLUMNS = [
    ("(srv)state_num_customers_in_queue", "(srv) # in queue"),
    ("(srv)state_num_customers_in_service", "(srv) # in service"),
    ("(srv)state_num_customers_in_system", "(srv) # in system"),
]

# Trigger highlighted in the per-inner figures (near a busy moment, clear fan-out).
HIGHLIGHT_TARGET = 3.5
COLORS = ("#4c78c8", "#d6604d", "#2ca02c")  # blue, red, green per inner k

DOCS = Path(__file__).resolve().parents[1]
STATIC = DOCS / "_static"


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
    env.set_rng("independent")  # each branch draws its own future
    env.set_outer_seed(SEED)
    env.set_triggering_objects(nested_id="srv")
    env.set_triggering_conditions({"on": "arrival", "frequency": 1})
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


# ----------------------------------------------------------------- helpers ---

def _series(rows, *, source=None, t_offset=0.0, t_max=None):
    """Extract an ``(xs, ys)`` step series of the queue metric from CSV rows."""

    xs, ys = [], []
    for row in rows:
        if source is not None and row.get("simulation_source") != source:
            continue
        value = row.get(METRIC)
        if value in (None, ""):
            continue
        t = float(row["t"]) - t_offset
        if t_max is not None and t > t_max:
            break
        xs.append(t)
        ys.append(float(value))
    return xs, ys


def _style(ax) -> None:
    ax.set_xlabel("time", fontsize=12)
    ax.set_ylabel(Y_LABEL, fontsize=12)
    ax.set_ylim(bottom=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _highlight_trigger(om: OutputManager):
    triggers = om.triggers()
    return min(triggers, key=lambda t: abs((t.branch_time or 0.0) - HIGHLIGHT_TARGET))


# ----------------------------------------------------------------- figures ---

def fig_outer_static(om: OutputManager) -> None:
    """Static plot of the outer queue length, with a dot at every trigger."""

    ox, oy = _series(om.export_outer_event_log())
    fig, ax = plt.subplots(figsize=(8.0, 3.5))
    ax.step(ox, oy, where="post", color="black", linewidth=1.8, label="outer path")

    def at(t):
        val = oy[0] if oy else 0
        for x, y in zip(ox, oy):
            if x <= t:
                val = y
            else:
                break
        return val

    ts = [info.branch_time or 0.0 for info in om.triggers()]
    ax.scatter(ts, [at(t) for t in ts], s=16, color="#9aa0a6", zorder=4,
               edgecolor="white", linewidth=0.4, label="trigger points")
    ax.set_xlim(left=0)
    ax.set_title("Outer simulation")
    _style(ax)
    ax.legend(loc="upper left", frameon=True, fontsize=10)
    fig.tight_layout()
    out = STATIC / "mm1-outer-static.svg"
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def fig_inner(om: OutputManager, *, all_inners: bool) -> None:
    """Static plot of one (or all) inner branch(es) at the highlight trigger.

    The time axis is relative to the trigger (the trigger point is at 0); the
    outer lead-in is grey, the inner branch(es) coloured.
    """

    info = _highlight_trigger(om)
    bt = info.branch_time or 0.0
    inner_ids = info.inner_ids if all_inners else [info.inner_ids[0]]

    fig, ax = plt.subplots(figsize=(8.0, 3.5))
    # outer lead-in (shared) from the first branch's outer rows
    ctx = om.export_inner_event_log(info.trigger_id, inner_ids[0])
    cx, cy = _series(ctx, source="outer", t_offset=bt)
    # state at the trigger point = the last outer value (the inner starts from it)
    fork_y = cy[-1] if cy else None
    if cx and fork_y is not None:
        # bridge the context up to the trigger point so the lines meet at time 0
        cx.append(0.0)
        cy.append(fork_y)
    if cx:
        ax.step(cx, cy, where="post", color="#888888", linewidth=2.0,
                label="outer path (context)")
    for k, color in zip(inner_ids, COLORS):
        rows = om.export_inner_event_log(info.trigger_id, k)
        ix, iy = _series(rows, source="inner", t_offset=bt)
        if fork_y is not None:
            # every inner starts at the trigger point with the outer state
            ix.insert(0, 0.0)
            iy.insert(0, fork_y)
        ax.step(ix, iy, where="post", color=color, linewidth=1.4,
                label=f"inner branch k={k}")
    ax.axvline(0.0, color="black", linewidth=0.8, linestyle=":", alpha=0.4)
    title = ("All inner branches" if all_inners else "A single inner branch")
    ax.set_title(f"{title} (trigger event {info.trigger_id})")
    ax.set_xlabel("time since trigger", fontsize=12)
    ax.set_ylabel(Y_LABEL, fontsize=12)
    ax.set_ylim(bottom=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(loc="upper left", frameon=True, fontsize=9)
    fig.tight_layout()
    name = "mm1-inner-all.svg" if all_inners else "mm1-inner-one.svg"
    out = STATIC / name
    fig.savefig(out, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", out)


def fig_interactive(run_dir: str) -> None:
    """Interactive outer plot: click a trigger point to toggle its inner branches."""

    out = STATIC / "mm1-interactive.html"
    write_dynamic_plot(
        run_dir, output_path=str(out),
        state_field=QUEUE_FIELD, resource_id="srv",
    )
    print("wrote", out)


# ------------------------------------------------------------------ tables ---

def _scroll_table(headers, rows) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = "\n".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows
    )
    return (
        '<div class="ns-dataset-scroll">\n'
        '<table class="ns-dataset-table">\n'
        f"<thead><tr>{th}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>\n</div>"
    )


def _num(v, nd=2):
    if v in (None, ""):
        return ""
    try:
        return f"{float(v):.{nd}f}"
    except (TypeError, ValueError):
        return str(v)


def _inject(marker: str, html: str) -> None:
    page = DOCS / "simple-example.md"
    text = page.read_text(encoding="utf-8")
    begin = f"<!-- {marker}:begin"
    end = f"<!-- {marker}:end -->"
    i = text.index("-->", text.index(begin)) + len("-->")
    j = text.index(end)
    page.write_text(text[:i] + "\n" + html + "\n" + text[j:], encoding="utf-8")
    print("injected", marker)


def table_inner(om: OutputManager) -> None:
    """One inner sample path (its outer lead-in, then the inner branch)."""

    info = _highlight_trigger(om)
    rows = [r for r in om.export_inner_event_log(info.trigger_id, info.inner_ids[0])
            if r.get(METRIC) not in (None, "")]
    # Keep the inner segment (the launched future) plus a little outer context
    # just before the trigger point, so the table shows the hand-off without the
    # whole history.
    before = [r for r in rows if r.get("simulation_source") == "outer"][-4:]
    inner = [r for r in rows if r.get("simulation_source") == "inner"]
    out = [
        (r.get("simulation_source"), _num(r.get("t")))
        + tuple(_num(r.get(col), 0) for col, _ in STATE_COLUMNS)
        + (r.get("queue_event"),)
        for r in before + inner
    ]
    # Caption naming the (trigger event, replication number) pair the table
    # shows, so the reader can tie it back to the outer sample path.
    caption = (
        '<p class="ns-dataset-caption"><em>Inner simulation with replication '
        f"number k&nbsp;=&nbsp;{info.inner_ids[0]} at trigger event "
        f"{info.trigger_id}.</em></p>"
    )
    html = caption + "\n" + _scroll_table(
        ["Simulation source", "Time"]
        + [header for _, header in STATE_COLUMNS]
        + ["Event"],
        out,
    )
    (STATIC / "mm1-table-inner.html").write_text(html + "\n", encoding="utf-8")
    _inject("mm1-table-inner", html)


def table_outer(om: OutputManager) -> None:
    """The outer sample path."""

    rows = om.export_outer_event_log()
    out = [
        (_num(r.get("t")),)
        + tuple(_num(r.get(col), 0) for col, _ in STATE_COLUMNS)
        + (r.get("queue_event"), r.get("cust_id"))
        for r in rows
        if r.get(METRIC) not in (None, "")
    ]
    html = _scroll_table(
        ["Time"]
        + [header for _, header in STATE_COLUMNS]
        + ["Event", "Customer"],
        out,
    )
    (STATIC / "mm1-table-outer.html").write_text(html + "\n", encoding="utf-8")
    _inject("mm1-table-outer", html)


def table_predictions(om: OutputManager) -> None:
    """Each triggering customer with the average outcome over its inner runs."""

    rows = om.export_outer_case_table()
    out = []
    for r in rows:
        if r.get("inner_num_branches") in (None, ""):
            continue
        wait = _num(r.get("inner_waiting_time_mean"))
        if wait == "":
            # A blank mean wait here is a true zero, not missing data: the
            # trigger fires on arrival, and when the server is idle at that
            # instant the customer enters service immediately (in the outer,
            # before the branch forks), so no inner branch records a later
            # service start and the per-branch waiting_time stays None.
            # Verified per branch: service_start is None while the service
            # completion is present, and the outer row at the trigger shows
            # 0 customers in service. Render the exact zero.
            in_service = r.get("(srv)state_num_customers_in_service")
            if in_service not in (None, "") and float(in_service) == 0:
                wait = _num(0.0)
        out.append(
            (
                r.get("cust_id"),
                _num(r.get("inner_anchor_arrival_time_mean")),
            )
            # system state at the trigger event (from the trigger row itself)
            + tuple(_num(r.get(col), 0) for col, _ in STATE_COLUMNS)
            + (
                r.get("inner_num_branches"),
                wait,
                _num(r.get("inner_service_completion_time_mean")),
            )
        )
    html = _scroll_table(
        ["Customer", "Arrival"]
        + [header for _, header in STATE_COLUMNS]
        + ["# inner branches", "Mean inner wait", "Mean inner service time"],
        out,
    )
    (STATIC / "mm1-table-pred.html").write_text(html + "\n", encoding="utf-8")
    _inject("mm1-table-pred", html)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = run_model(os.path.join(tmp, "out"))
        om = OutputManager(run_dir)
        fig_outer_static(om)
        fig_interactive(run_dir)
        fig_inner(om, all_inners=False)
        fig_inner(om, all_inners=True)
        table_inner(om)
        table_outer(om)
        table_predictions(om)


if __name__ == "__main__":
    main()
