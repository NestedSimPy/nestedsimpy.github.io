"""Run a simple M/M/1 queue under the SimPy branching API.

Usage:
    python examples/run_mm1_simpy.py"""

from __future__ import annotations

from _imports import *

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
from tools.postprocess_helpers import wait_time_hook

DEFAULT_MM1_OUT_DIR = DEFAULT_OUT_ROOT / "mm1_simpy"


def customer(
    env: NestedEnvironment, resource: NestedResource, service_rate: float
) -> Iterator[events.Event]:
    """Service discipline for a single customer.

    Args:
        env: Nested environment orchestrating the simulation.
        resource: Instrumented server (``NestedResource``) this customer uses.
        service_rate: Exponential service rate ``μ`` (customers per unit time).

    Yields:
        SimPy events describing the request, service start, and completion.
        The ``NestedResource`` records each transition for nested analysis.
    """

    with resource.request() as req:
        yield req
        yield env.nested_timeout(
            {"distribution": "exponential", "lambda": service_rate},
            label="service_time",
        )


def arrival_process(
    env: NestedEnvironment,
    resource: NestedResource,
    arrival_rate: float,
    service_rate: float,
) -> Iterator[events.Event]:
    """Infinite-source arrival generator for the M/M/1 queue.

    Args:
        env: Nested environment orchestrating the simulation.
        resource: Server that all arrivals will visit.
        arrival_rate: Exponential arrival rate ``λ``.
        service_rate: Service rate passed to :func:`customer`.

    Yields:
        SimPy events representing successive inter-arrivals and the launch of
        a customer process for each arrival.
    """

    while True:
        yield env.nested_timeout(
            {"distribution": "exponential", "lambda": arrival_rate},
            label="interarrival",
        )
        env.process(customer(env, resource, service_rate))


def preview_trace(path: Path, limit: int = 5) -> None:
    """Print the first ``limit`` lines of ``path`` to STDOUT.

    Args:
        path (Path): Trace file produced by the toolkit.
        limit (int): Number of lines to preview.
    """

    opener = gzip.open if path.suffix == ".gz" else Path.open
    with opener(path, "rt", encoding="utf-8") as fh:  # type: ignore[arg-type]
        for _, line in zip(range(limit), fh):
            print(line.rstrip())


def _latest_run_dir(out_root: Path) -> Path:
    run_dirs = [path for path in out_root.iterdir() if path.is_dir()]
    if not run_dirs:
        raise FileNotFoundError(f"No runs found under {out_root}")
    return max(run_dirs, key=lambda path: path.stat().st_mtime)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the branching M/M/1 demo."""

    parser = argparse.ArgumentParser(
        description="Run the nested-sim M/M/1 branching demo."
    )
    parser.add_argument(
        "--arrival-rate",
        type=float,
        default=3.0,
        help="Exponential arrival rate λ.",
    )
    parser.add_argument(
        "--service-rate",
        type=float,
        default=4.0,
        help="Exponential service rate μ.",
    )
    parser.add_argument(
        "--outer-time",
        type=float,
        default=10.0,
        help="Outer-run time horizon.",
    )
    parser.add_argument(
        "--outer-arrivals",
        type=int,
        default=None,
        help="Optional outer arrival limit.",
    )
    parser.add_argument(
        "--branches",
        type=int,
        default=2,
        help="Number of child branches spawned per trigger.",
    )
    parser.add_argument(
        "--inner-horizon",
        type=float,
        default=5.0,
        help="Inner branch time horizon.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1234,
        help="Outer random seed.",
    )
    add_reporting_cli(
        parser,
        default_out_dir=DEFAULT_MM1_OUT_DIR,
        default_state_field="state_num_customers_in_system",
        default_resource_id="srv",
    )
    return parser.parse_args()


def main() -> None:
    """Configure the M/M/1 branching demo, then run and preview the trace."""

    args = parse_args()
    env = NestedEnvironment()
    resource = NestedResource(env, capacity=1, nested_id="srv")
    env.process(
        arrival_process(
            env,
            resource,
            arrival_rate=args.arrival_rate,
            service_rate=args.service_rate,
        )
    )

    # Output options first.
    mm1_dir = args.out_dir
    mm1_dir.mkdir(parents=True, exist_ok=True)
    env.set_output_options(out_dir=str(mm1_dir), gzip_trace=False)

    # Outer settings.
    env.set_rng("independent")
    env.set_outer_seed(args.seed)
    env.set_nested_triggering_objects(nested_id="srv")
    env.set_nesting_conditions(
        {
            "on": "arrival",
            "frequency": 1,
        }
    )
    env.set_outer_stopping_condition(
        timeout=args.outer_time,
        max_arrivals=args.outer_arrivals,
    )

    # Post-processing: generate per-branch wait times (user_waits.csv + metrics json).
    def _post_hook(outer_dir, exports_dir, manifest, **opts):
        return {"waits": wait_time_hook(outer_dir, exports_dir, manifest, **opts)}

    env.set_postprocessor(_post_hook, output_name="user_metrics.json")

    # Inner settings.
    env.set_inner_repetitions(args.branches)
    env.set_inner_stopping_condition(
        relative_time=args.inner_horizon,
        triggering_customer_departs=True,
    )
    env.nested_run()

    latest_outer = finalize_reporting(
        mm1_dir,
        postprocess=args.postprocess,
        plot_static=args.plot_static,
        plot_dynamic=args.plot_dynamic,
        state_field=args.state_field,
        resource_id=args.resource_id,
    )
    trace_path = resolve_raw_run_dir(latest_outer) / "outer" / "trace.jsonl"
    if not trace_path.exists():
        trace_path = trace_path.with_suffix(".jsonl.gz")
    print("\nPreviewing", display_path(trace_path))
    preview_trace(trace_path)


if __name__ == "__main__":
    main()
