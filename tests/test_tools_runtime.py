import asyncio
import subprocess
import sys
from pathlib import Path

from diligence.models import QueryPlan, SearchCandidate, SearchItem, SearchResult
from prebuild_engine.build_or_not import run_build_or_not
from prebuild_engine.find_tools import run_find_tools
from prebuild_engine.models import (
    ArtifactPaths,
    BuildOrNotCandidate,
    BuildOrNotResult,
    CandidateEvidence,
    CorroborationSummary,
    ExaSearchHit,
    FindToolsResult,
)
from prebuild_engine.renderers import (
    render_build_or_not_canonical_report,
    render_build_or_not_html_report,
    render_find_tools_canonical_report,
    render_find_tools_html_report,
)


def test_build_or_not_writes_artifacts_and_prefers_reuse(tmp_path):
    async def fake_search_projects(*args, **kwargs):
        del args, kwargs
        plan = QueryPlan(
            query="agent marketplace for software bounties",
            depth="deep",
            intent="idea_market_discovery",
            facets={
                "functional": "agent marketplace",
                "technical": "agent skill mcp",
                "market": "software bounty marketplace",
                "research": "agent marketplace",
            },
            query_clusters={"solution_form": ["agent marketplace"]},
            enabled_sources=["github", "repo_posts"],
            suppressed_sources=["npm"],
            source_queries={"github": ["agent marketplace"]},
            context7_attempted=False,
            context7_status="planned_optional_agent_side",
        )
        candidate = SearchCandidate(
            canonical_name="acme/agent-market",
            artifact_type="repo",
            url="https://github.com/acme/agent-market",
            summary="Open source marketplace for autonomous agent bidding.",
            sources=["github", "repo_posts"],
            fit_labels=["marketplace", "agent_platform"],
            score=1.45,
            evidence=[
                SearchItem(
                    title="acme/agent-market",
                    url="https://github.com/acme/agent-market",
                    source="github",
                    artifact_type="repo",
                    summary="Primary repo evidence.",
                ),
                SearchItem(
                    title="acme/agent-market",
                    url="https://github.com/acme/agent-market",
                    source="repo_posts",
                    artifact_type="repo",
                    summary="Repository catalog evidence.",
                ),
            ],
        )
        return SearchResult(query=plan.query, query_plan=plan, candidates=[candidate], exploration_urls=[], warnings=[])

    async def fake_search_exa(queries):
        assert queries
        return (
            [
                ExaSearchHit(
                    query_family="broad",
                    query="agent marketplace for software bounties",
                    title="Acme Agent Market",
                    url="https://acme.example.com",
                    summary="Bids on software tasks with autonomous agents.",
                    published_date="2026-05-01",
                    author="Acme",
                    score=0.91,
                    evidence_kind="primary",
                )
            ],
            [],
        )

    result = asyncio.run(
        run_build_or_not(
            "agent marketplace for software bounties",
            run_id="test-run",
            artifacts_root=tmp_path,
            search_projects_fn=fake_search_projects,
            search_exa_fn=fake_search_exa,
        )
    )

    assert result.verdict == "reuse_existing"
    assert result.confidence == "high"
    assert result.leading_candidates[0].name == "acme/agent-market"
    assert Path(result.artifacts.result_json).is_file()
    assert Path(result.artifacts.canonical_report).is_file()
    assert Path(result.artifacts.html_report).is_file()
    assert Path(result.artifacts.audit_bundle, "manifest.json").is_file()


def test_build_or_not_does_not_recommend_greenfield_without_exa(tmp_path):
    async def fake_search_projects(*args, **kwargs):
        del args, kwargs
        plan = QueryPlan(
            query="novel idea validation runtime",
            depth="deep",
            intent="general",
            facets={
                "functional": "idea validation runtime",
                "technical": "idea validation runtime",
                "market": "idea validation runtime",
                "research": "idea validation runtime",
            },
            query_clusters={"primary": ["idea validation runtime"]},
            enabled_sources=["github"],
            suppressed_sources=["npm"],
            source_queries={"github": ["idea validation runtime"]},
            context7_attempted=False,
            context7_status="skipped_not_technical",
        )
        return SearchResult(query=plan.query, query_plan=plan, candidates=[], exploration_urls=[], warnings=[])

    async def fake_search_exa(_queries):
        return [], ["EXA_API_KEY is not set; Exa-first discovery was skipped."]

    result = asyncio.run(
        run_build_or_not(
            "novel idea validation runtime",
            run_id="no-exa",
            artifacts_root=tmp_path,
            search_projects_fn=fake_search_projects,
            search_exa_fn=fake_search_exa,
        )
    )

    assert result.verdict == "needs_manual_review"
    assert result.confidence == "low"


def test_find_tools_recommends_best_fit(tmp_path):
    async def fake_search_projects(*args, **kwargs):
        del args, kwargs
        plan = QueryPlan(
            query="python framework for agent orchestration",
            depth="deep",
            intent="technical_reuse",
            facets={
                "functional": "agent orchestration",
                "technical": "python framework agent orchestration",
                "market": "developer tool",
                "research": "agent orchestration",
            },
            query_clusters={"primary": ["agent orchestration"]},
            enabled_sources=["github", "pypi"],
            suppressed_sources=["hn"],
            source_queries={"github": ["agent orchestration"], "pypi": ["langgraph"]},
            context7_attempted=False,
            context7_status="planned_optional_agent_side",
        )
        return SearchResult(
            query=plan.query,
            query_plan=plan,
            candidates=[
                SearchCandidate(
                    canonical_name="langgraph",
                    artifact_type="package",
                    url="https://pypi.org/project/langgraph",
                    summary="Agent orchestration framework with Python package distribution.",
                    sources=["pypi", "github"],
                    fit_labels=["agent_platform", "open_source"],
                    score=1.32,
                    evidence=[
                        SearchItem(
                            title="langgraph",
                            url="https://pypi.org/project/langgraph",
                            source="pypi",
                            artifact_type="package",
                            summary="Package evidence.",
                        ),
                        SearchItem(
                            title="langgraph",
                            url="https://github.com/langchain-ai/langgraph",
                            source="github",
                            artifact_type="repo",
                            summary="Repo evidence.",
                        ),
                    ],
                ),
                SearchCandidate(
                    canonical_name="crewai",
                    artifact_type="package",
                    url="https://pypi.org/project/crewai",
                    summary="Multi-agent workflow framework.",
                    sources=["pypi"],
                    fit_labels=["agent_platform"],
                    score=0.91,
                    evidence=[
                        SearchItem(
                            title="crewai",
                            url="https://pypi.org/project/crewai",
                            source="pypi",
                            artifact_type="package",
                            summary="Package evidence.",
                        )
                    ],
                ),
            ],
            exploration_urls=[],
            warnings=[],
        )

    async def fake_search_exa(_queries):
        return (
            [
                ExaSearchHit(
                    query_family="broad",
                    query="python framework for agent orchestration",
                    title="LangGraph docs",
                    url="https://langchain-ai.github.io/langgraph/",
                    summary="Build stateful, multi-actor agent systems.",
                    published_date="2026-05-01",
                    author="LangChain",
                    score=0.89,
                    evidence_kind="primary",
                )
            ],
            [],
        )

    result = asyncio.run(
        run_find_tools(
            "python framework for agent orchestration",
            run_id="find-tools-best-fit",
            artifacts_root=tmp_path,
            search_projects_fn=fake_search_projects,
            search_exa_fn=fake_search_exa,
        )
    )

    assert result.decision == "best_fit_found"
    assert result.best_fit is not None
    assert result.best_fit.name == "langgraph"
    assert Path(result.artifacts.result_json).is_file()


def test_find_tools_requires_manual_review_without_exa(tmp_path):
    async def fake_search_projects(*args, **kwargs):
        del args, kwargs
        plan = QueryPlan(
            query="mcp server for startup research",
            depth="deep",
            intent="technical_reuse",
            facets={
                "functional": "startup research",
                "technical": "mcp startup research",
                "market": "developer tool",
                "research": "startup research",
            },
            query_clusters={"primary": ["startup research"]},
            enabled_sources=["github"],
            suppressed_sources=["hn"],
            source_queries={"github": ["startup research"]},
            context7_attempted=False,
            context7_status="planned_optional_agent_side",
        )
        return SearchResult(query=plan.query, query_plan=plan, candidates=[], exploration_urls=[], warnings=[])

    async def fake_search_exa(_queries):
        return [], ["EXA_API_KEY is not set; Exa-first discovery was skipped."]

    result = asyncio.run(
        run_find_tools(
            "mcp server for startup research",
            run_id="find-tools-no-exa",
            artifacts_root=tmp_path,
            search_projects_fn=fake_search_projects,
            search_exa_fn=fake_search_exa,
        )
    )

    assert result.decision == "needs_manual_review"
    assert result.confidence == "low"


def test_renderers_match_snapshots():
    plan = QueryPlan(
        query="agent marketplace for software bounties",
        depth="deep",
        intent="idea_market_discovery",
        facets={
            "functional": "agent marketplace",
            "technical": "agent skill mcp",
            "market": "software bounty marketplace",
            "research": "agent marketplace",
        },
        query_clusters={"solution_form": ["agent marketplace"]},
        enabled_sources=["github"],
        suppressed_sources=["npm"],
        source_queries={"github": ["agent marketplace"]},
        context7_attempted=False,
        context7_status="planned_optional_agent_side",
    )
    structured = SearchResult(
        query="agent marketplace for software bounties",
        query_plan=plan,
        candidates=[],
        exploration_urls=[],
        warnings=[],
    )
    candidate = BuildOrNotCandidate(
        name="acme/agent-market",
        artifact_type="repo",
        url="https://github.com/acme/agent-market",
        summary="Open source marketplace for autonomous agent bidding.",
        fit_labels=["marketplace", "agent_platform"],
        confidence="high",
        corroboration=CorroborationSummary(
            primary_count=2,
            secondary_count=1,
            discussion_count=0,
            structured_sources=["github", "repo_posts"],
            web_hits=1,
        ),
        strength_score=2.75,
        rationale="1 Exa corroboration hit(s); structured sources: github, repo_posts; fit labels: marketplace, agent_platform",
        evidence=[
            CandidateEvidence(
                kind="primary",
                source="github",
                title="acme/agent-market",
                url="https://github.com/acme/agent-market",
                summary="Repo evidence",
            )
        ],
    )
    exa_hit = ExaSearchHit(
        query_family="broad",
        query="agent marketplace for software bounties",
        title="Acme Agent Market",
        url="https://acme.example.com",
        summary="Bids on software tasks with autonomous agents.",
        published_date="2026-05-01",
        author="Acme",
        score=0.91,
        evidence_kind="primary",
    )
    build_result = BuildOrNotResult(
        capability="agent marketplace for software bounties",
        generated_at="2026-05-14T10:00:00+00:00",
        run_id="build-or-not-test-1234",
        verdict="reuse_existing",
        confidence="high",
        verdict_rationale="A credible existing solution surfaced with corroboration across web discovery and structured sources.",
        recommended_action="Default to the top existing candidate first. Only build new capability around gaps that remain after evaluation.",
        evidence_policy="Important claims should cite primary evidence when available, prefer two corroborating signals when possible, and fold freshness into confidence.",
        query_plan=plan,
        exa_queries=[{"family": "broad", "query": "agent marketplace for software bounties"}],
        leading_candidates=[candidate],
        exa_hits=[exa_hit],
        structured_search=structured,
        warnings=["Directory seed search timed out."],
        artifacts=ArtifactPaths(
            output_dir="/tmp/build-or-not-test-1234",
            result_json="/tmp/build-or-not-test-1234/result.json",
            canonical_report="/tmp/build-or-not-test-1234/canonical-report.md",
            html_report="/tmp/build-or-not-test-1234/report.html",
            audit_bundle="/tmp/build-or-not-test-1234/audit",
        ),
    )
    find_result = FindToolsResult(
        query="python framework for agent orchestration",
        generated_at="2026-05-14T11:00:00+00:00",
        run_id="find-tools-test-5678",
        decision="best_fit_found",
        confidence="medium",
        selection_rationale="A strongest candidate surfaced with enough corroboration to recommend it as the current best fit.",
        recommended_artifact_type="package",
        query_plan=plan.model_copy(
            update={
                "query": "python framework for agent orchestration",
                "intent": "technical_reuse",
                "facets": {
                    "functional": "agent orchestration",
                    "technical": "python framework agent orchestration",
                    "market": "developer tool",
                    "research": "agent orchestration",
                },
            }
        ),
        exa_queries=[{"family": "broad", "query": "python framework for agent orchestration"}],
        best_fit=BuildOrNotCandidate(
            name="langgraph",
            artifact_type="package",
            url="https://pypi.org/project/langgraph",
            summary="Agent orchestration framework with Python package distribution.",
            fit_labels=["agent_platform", "open_source"],
            confidence="medium",
            corroboration=CorroborationSummary(
                primary_count=1,
                secondary_count=1,
                discussion_count=0,
                structured_sources=["pypi", "github"],
                web_hits=1,
            ),
            strength_score=1.92,
            rationale="1 Exa corroboration hit(s); structured sources: pypi, github; fit labels: agent_platform, open_source",
            evidence=[
                CandidateEvidence(
                    kind="primary",
                    source="pypi",
                    title="langgraph",
                    url="https://pypi.org/project/langgraph",
                    summary="Package evidence",
                )
            ],
        ),
        alternatives=[
            BuildOrNotCandidate(
                name="crewAI",
                artifact_type="package",
                url="https://pypi.org/project/crewai",
                summary="Multi-agent workflow framework.",
                fit_labels=["agent_platform"],
                confidence="medium",
                corroboration=CorroborationSummary(
                    primary_count=1,
                    secondary_count=0,
                    discussion_count=0,
                    structured_sources=["pypi"],
                    web_hits=0,
                ),
                strength_score=1.45,
                rationale="structured sources: pypi; fit labels: agent_platform",
                evidence=[],
            ),
            BuildOrNotCandidate(
                name="AutoGen",
                artifact_type="repo",
                url="https://github.com/microsoft/autogen",
                summary="Open source framework for agentic workflows.",
                fit_labels=["agent_platform", "open_source"],
                confidence="medium",
                corroboration=CorroborationSummary(
                    primary_count=1,
                    secondary_count=1,
                    discussion_count=1,
                    structured_sources=["github", "repo_posts"],
                    web_hits=0,
                ),
                strength_score=1.41,
                rationale="structured sources: github, repo_posts; fit labels: agent_platform, open_source",
                evidence=[],
            ),
        ],
        near_misses=[
            BuildOrNotCandidate(
                name="Temporal",
                artifact_type="product",
                url="https://temporal.io",
                summary="Workflow engine with adjacent orchestration primitives but not an agent-first framework.",
                fit_labels=[],
                confidence="low",
                corroboration=CorroborationSummary(
                    primary_count=1,
                    secondary_count=0,
                    discussion_count=0,
                    structured_sources=["github"],
                    web_hits=0,
                ),
                strength_score=0.88,
                rationale="Adjacent workflow engine, not agent-first.",
                evidence=[],
            )
        ],
        exa_hits=[
            ExaSearchHit(
                query_family="broad",
                query="python framework for agent orchestration",
                title="LangGraph docs",
                url="https://langchain-ai.github.io/langgraph/",
                summary="Build stateful, multi-actor agent systems.",
                published_date="2026-05-01",
                author="LangChain",
                score=0.89,
                evidence_kind="primary",
            )
        ],
        structured_search=structured.model_copy(update={"query": "python framework for agent orchestration"}),
        warnings=[],
        artifacts=ArtifactPaths(
            output_dir="/tmp/find-tools-test-5678",
            result_json="/tmp/find-tools-test-5678/result.json",
            canonical_report="/tmp/find-tools-test-5678/canonical-report.md",
            html_report="/tmp/find-tools-test-5678/report.html",
            audit_bundle="/tmp/find-tools-test-5678/audit",
        ),
    )

    fixtures = Path(__file__).parent / "fixtures"
    assert render_build_or_not_canonical_report(build_result) == (fixtures / "build_or_not_report.md").read_text(encoding="utf-8")
    assert render_build_or_not_html_report(build_result) == (fixtures / "build_or_not_report.html").read_text(encoding="utf-8")
    assert render_find_tools_canonical_report(find_result) == (fixtures / "find_tools_report.md").read_text(encoding="utf-8")
    assert render_find_tools_html_report(find_result) == (fixtures / "find_tools_report.html").read_text(encoding="utf-8")


def test_skill_wrappers_have_help_output():
    skill_root = Path(__file__).resolve().parents[1] / "skills" / "tools"
    for script in [
        skill_root / "build-or-not" / "scripts" / "run.py",
        skill_root / "find-tools" / "scripts" / "run.py",
    ]:
        completed = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0
        assert "usage:" in completed.stdout.lower()
