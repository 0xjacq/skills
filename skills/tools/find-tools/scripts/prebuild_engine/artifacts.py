from __future__ import annotations

import json
from pathlib import Path

from prebuild_engine.models import ArtifactPaths, AuditManifest, BuildOrNotResult, FindToolsResult
from prebuild_engine.renderers import (
    render_build_or_not_canonical_report,
    render_build_or_not_html_report,
    render_find_tools_canonical_report,
    render_find_tools_html_report,
    write_text,
)


def default_runs_root(base_dir: Path | None = None) -> Path:
    root = (base_dir or Path.cwd()) / ".cache" / "skills-tools"
    root.mkdir(parents=True, exist_ok=True)
    return root


def artifact_paths(tool_name: str, run_id: str, *, base_dir: Path | None = None) -> ArtifactPaths:
    output_dir = default_runs_root(base_dir) / tool_name / run_id
    return ArtifactPaths(
        output_dir=str(output_dir),
        result_json=str(output_dir / "result.json"),
        canonical_report=str(output_dir / "canonical-report.md"),
        html_report=str(output_dir / "report.html"),
        audit_bundle=str(output_dir / "audit"),
    )


def write_build_or_not_artifacts(result: BuildOrNotResult) -> BuildOrNotResult:
    output_dir = Path(result.artifacts.output_dir)
    audit_dir = Path(result.artifacts.audit_bundle)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    write_text(Path(result.artifacts.canonical_report), render_build_or_not_canonical_report(result))
    write_text(Path(result.artifacts.html_report), render_build_or_not_html_report(result))
    Path(result.artifacts.result_json).write_text(
        result.model_dump_json(indent=2),
        encoding="utf-8",
    )

    (audit_dir / "exa-hits.json").write_text(
        json.dumps([item.model_dump(mode="json") for item in result.exa_hits], indent=2),
        encoding="utf-8",
    )
    (audit_dir / "structured-search.json").write_text(
        result.structured_search.model_dump_json(indent=2),
        encoding="utf-8",
    )
    manifest = AuditManifest(
        tool_name="build-or-not",
        run_id=result.run_id,
        generated_at=result.generated_at,
        query=result.capability,
        decision=result.verdict,
        confidence=result.confidence,
        files={
            "result_json": result.artifacts.result_json,
            "canonical_report": result.artifacts.canonical_report,
            "html_report": result.artifacts.html_report,
            "exa_hits": str(audit_dir / "exa-hits.json"),
            "structured_search": str(audit_dir / "structured-search.json"),
        },
        warnings=result.warnings,
    )
    (audit_dir / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return result


def write_find_tools_artifacts(result: FindToolsResult) -> FindToolsResult:
    output_dir = Path(result.artifacts.output_dir)
    audit_dir = Path(result.artifacts.audit_bundle)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    write_text(Path(result.artifacts.canonical_report), render_find_tools_canonical_report(result))
    write_text(Path(result.artifacts.html_report), render_find_tools_html_report(result))
    Path(result.artifacts.result_json).write_text(
        result.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (audit_dir / "exa-hits.json").write_text(
        json.dumps([item.model_dump(mode="json") for item in result.exa_hits], indent=2),
        encoding="utf-8",
    )
    (audit_dir / "structured-search.json").write_text(
        result.structured_search.model_dump_json(indent=2),
        encoding="utf-8",
    )
    manifest = AuditManifest(
        tool_name="find-tools",
        run_id=result.run_id,
        generated_at=result.generated_at,
        query=result.query,
        decision=result.decision,
        confidence=result.confidence,
        files={
            "result_json": result.artifacts.result_json,
            "canonical_report": result.artifacts.canonical_report,
            "html_report": result.artifacts.html_report,
            "exa_hits": str(audit_dir / "exa-hits.json"),
            "structured_search": str(audit_dir / "structured-search.json"),
        },
        warnings=result.warnings,
    )
    (audit_dir / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return result
