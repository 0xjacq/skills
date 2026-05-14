from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from prebuild_engine.build_or_not import run_build_or_not
from prebuild_engine.find_tools import run_find_tools

app = typer.Typer(
    no_args_is_help=True,
    help="Local runtime for the published `build-or-not` and `find-tools` skills.",
)
console = Console()


@app.command("build-or-not")
def build_or_not_cmd(
    capability: Annotated[str, typer.Argument(help="Capability, product idea, or tool concept to assess.")],
    limit: Annotated[int, typer.Option("--limit", min=1, max=12, help="Maximum leading candidates to keep.")] = 8,
    run_id: Annotated[str | None, typer.Option("--run-id", help="Optional stable run id.")] = None,
    artifacts_root: Annotated[
        Path | None,
        typer.Option("--artifacts-root", help="Optional directory where runtime artifacts should be written."),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Emit the full machine-readable runtime result.")] = False,
) -> None:
    result = asyncio.run(
        run_build_or_not(
            capability,
            limit=limit,
            run_id=run_id,
            artifacts_root=artifacts_root,
        )
    )
    if json_output:
        console.print_json(result.model_dump_json())
        return
    console.print(f"build-or-not: verdict={result.verdict} confidence={result.confidence}")
    console.print(result.verdict_rationale)
    console.print(f"html: {result.artifacts.html_report}")
    console.print(f"json: {result.artifacts.result_json}")
    console.print(f"audit: {result.artifacts.audit_bundle}")


@app.command("find-tools")
def find_tools_cmd(
    query: Annotated[str, typer.Argument(help="Capability or tool query to satisfy.")],
    limit: Annotated[int, typer.Option("--limit", min=1, max=12, help="Maximum candidate pool to keep.")] = 8,
    run_id: Annotated[str | None, typer.Option("--run-id", help="Optional stable run id.")] = None,
    artifacts_root: Annotated[
        Path | None,
        typer.Option("--artifacts-root", help="Optional directory where runtime artifacts should be written."),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Emit the full machine-readable runtime result.")] = False,
) -> None:
    result = asyncio.run(
        run_find_tools(
            query,
            limit=limit,
            run_id=run_id,
            artifacts_root=artifacts_root,
        )
    )
    if json_output:
        console.print_json(result.model_dump_json())
        return
    console.print(f"find-tools: decision={result.decision} confidence={result.confidence}")
    console.print(result.selection_rationale)
    if result.best_fit is not None:
        console.print(f"best fit: {result.best_fit.name} ({result.best_fit.artifact_type})")
    console.print(f"html: {result.artifacts.html_report}")
    console.print(f"json: {result.artifacts.result_json}")
    console.print(f"audit: {result.artifacts.audit_bundle}")
