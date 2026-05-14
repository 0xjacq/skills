from __future__ import annotations

import asyncio
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from diligence.adapters import ADAPTERS
from diligence.collect import collect_all, doctor, source_search
from diligence.models import CollectResult, DoctorResult, SearchResult, SourceResult
from diligence.search import search_projects

app = typer.Typer(no_args_is_help=True, help="Codex-oriented pre-build diligence source collector.")
console = Console()


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Natural-language search query for a reranked shortlist.")],
    depth: Annotated[str, typer.Option("--depth", help="Search preset: quick or deep.")] = "quick",
    mode: Annotated[
        str,
        typer.Option("--mode", help="Search mode: auto, idea-market, technical-reuse, market-discovery, or research-discovery."),
    ] = "auto",
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, max=50, help="Max ranked candidates.")] = 10,
    json_output: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
) -> None:
    """Plan, route, retrieve, and rerank a shortlist."""
    result = asyncio.run(search_projects(query, depth=depth, limit=limit, mode=mode))
    _emit_search(result, json_output)


@app.command()
def collect(
    query: Annotated[str, typer.Argument(help="Natural-language capability query.")],
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, max=50, help="Max items per source.")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
) -> None:
    """Query all structured MVP sources."""
    result = asyncio.run(collect_all(query, limit=limit))
    _emit_collect(result, json_output)


@app.command()
def source(
    source_name: Annotated[str, typer.Argument(help="One source name, e.g. github, repo_posts, hn.")],
    query: Annotated[str, typer.Argument(help="Search query or exact package name for PyPI.")],
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, max=50, help="Max returned items.")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
) -> None:
    """Query one source adapter."""
    result = asyncio.run(source_search(source_name, query, limit=limit))
    _emit_source(result, json_output)


@app.command()
def sources(json_output: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False) -> None:
    """List available sources."""
    if json_output:
        console.print_json(data={"sources": sorted(ADAPTERS)})
        return
    console.print("\n".join(sorted(ADAPTERS)))


def doctor_cmd(json_output: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False) -> None:
    """Check local runtime assumptions."""
    _emit_doctor(doctor(), json_output)


app.command(name="doctor")(doctor_cmd)


def _emit_collect(result: CollectResult, json_output: bool) -> None:
    if json_output:
        console.print_json(result.model_dump_json())
        return
    _print_items(result.items, f"Results for: {result.query}")
    _print_warnings(result.warnings)


def _emit_search(result: SearchResult, json_output: bool) -> None:
    if json_output:
        console.print_json(result.model_dump_json())
        return
    console.print(
        f"search: intent={result.query_plan.intent} depth={result.query_plan.depth} "
        f"context7={result.query_plan.context7_status}"
    )
    _print_candidates(result.candidates, f"Shortlist for: {result.query}")
    if result.exploration_urls:
        _print_items(result.exploration_urls, "Exploration URLs")
    _print_warnings(result.warnings)


def _emit_source(result: SourceResult, json_output: bool) -> None:
    if json_output:
        console.print_json(result.model_dump_json())
        return
    _print_items(result.items, f"{result.source}: {result.query}")
    _print_warnings(result.warnings)


def _emit_doctor(result: DoctorResult, json_output: bool) -> None:
    if json_output:
        console.print_json(result.model_dump_json())
        return
    status = "ok" if result.ok else "needs attention"
    console.print(f"doctor: {status}")
    for name, value in result.checks.items():
        console.print(f"- {name}: {value}")
    _print_warnings(result.warnings)


def _print_items(items, title: str) -> None:
    table = Table(title=title)
    table.add_column("source")
    table.add_column("type")
    table.add_column("title")
    table.add_column("signals")
    table.add_column("url")
    for item in items:
        signal_parts = []
        for field in ("stars", "points", "downloads", "forks", "last_updated"):
            value = getattr(item.signals, field)
            if value not in (None, ""):
                signal_parts.append(f"{field}={value}")
        table.add_row(item.source, item.artifact_type, item.title, " ".join(signal_parts), item.url)
    console.print(table)


def _print_candidates(candidates, title: str) -> None:
    table = Table(title=title)
    table.add_column("score")
    table.add_column("type")
    table.add_column("name")
    table.add_column("fit")
    table.add_column("sources")
    table.add_column("url")
    for candidate in candidates:
        table.add_row(
            f"{candidate.score:.2f}",
            candidate.artifact_type,
            candidate.canonical_name,
            ",".join(candidate.fit_labels),
            ",".join(candidate.sources),
            candidate.url,
        )
    console.print(table)


def _print_warnings(warnings: list[str]) -> None:
    if not warnings:
        return
    console.print("Warnings:")
    for warning in warnings:
        console.print(f"- {warning}")
