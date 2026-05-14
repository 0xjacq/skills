---
name: "grill-me"
description: "Stress-test a plan or design through one question at a time. Use when the user explicitly wants to be grilled on an architecture, API, migration, or implementation plan instead of getting a finished answer immediately."
argument-hint: "<plan-or-design>"
disable-model-invocation: true
user-invocable: true
---

# Grill Me

Interview the user relentlessly about a plan or design until you reach shared understanding.

## Core Rules

- Ask one question at a time.
- For every question, provide your recommended answer.
- Resolve upstream decisions before downstream details.
- Keep drilling until assumptions, interfaces, risks, and success criteria are explicit.
- If a question can be answered by exploring the codebase or artifacts, inspect them instead of asking.

## Flow

1. Restate the plan in operational terms.
2. Identify the highest-leverage unresolved decision.
3. Ask exactly one question about that decision.
4. Provide the recommended answer immediately after the question.
5. Wait for the user's answer before moving on.
6. Use the answer to choose the next branch in the design tree.
7. Repeat until the plan is concrete, internally consistent, and implementation-ready.

## What to Prioritize

- Goals, constraints, and success criteria before implementation details
- External interfaces, data contracts, and invariants before internal structure
- Failure modes, rollback paths, migrations, observability, and testing early
- Ambiguity, overloaded terms, and hidden assumptions
- Questions whose answers constrain the most later decisions

## Codebase-First Rule

Before asking about existing behavior, architecture, naming, integrations, schema, or conventions, inspect the repository and answer from evidence when possible.

Only ask the user when the answer depends on intent, priority, product tradeoffs, or missing external context.
