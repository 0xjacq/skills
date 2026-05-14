"""Pre-build diligence CLI package."""

__version__ = "0.1.0"

from diligence.query_intent import QueryIntent, classify_query_intent, should_use_context7
from diligence.search import build_query_plan, search_projects

__all__ = [
    "QueryIntent",
    "build_query_plan",
    "classify_query_intent",
    "search_projects",
    "should_use_context7",
    "__version__",
]
