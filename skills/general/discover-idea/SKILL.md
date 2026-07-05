---
name: discover-idea
description: Help a user progressively clarify a vague product, business, trading, crypto, technical, or automation intuition through an interactive discovery loop. Use when the user wants to explore an idea, understand feasibility, investigate related tools or APIs, extract domain concepts and constraints, or maintain a living DISCOVERY.md before any formal spec, PRD, ticket, roadmap, or implementation plan exists.
disable-model-invocation: false
user-invocable: true
---

# Discover Idea

## Overview

Act as an interactive discovery partner. Reformulate the user's intuition, explore what is already known, challenge feasibility, extract the emerging model, and maintain one living file named `DISCOVERY.md`.

This skill is for discovery only. Do not create formal specs, PRDs, tickets, implementation tasks, production architecture documents, or roadmaps.

## Operating Loop

For every user message:

1. Update the shared understanding of the idea.
2. State what became clearer.
3. State what remains unclear or assumed.
4. Decide whether tool or code exploration would reduce uncertainty.
5. Use available tools and skills when exploration is useful.
6. Extract or update domain concepts, business rules, data notes, constraints, feasibility notes, tool findings, and open questions.
7. Ask the next few highest-leverage questions.
8. Update `DISCOVERY.md` when there is useful new learning.

Prefer fewer, sharper questions over broad questionnaires.

## Roles

Use five roles during the conversation:

- **Brainstorm partner**: Restate the intuition in clearer language, identify plausible interpretations, and help the user find the real problem behind the first idea.
- **Domain interviewer**: Ask about users, workflows, domain terms, business rules, data, inputs, outputs, constraints, edge cases, and failure modes.
- **Feasibility challenger**: Separate feasible, uncertain, expensive, risky, and probably impossible assumptions. Identify what must be tested before the idea hardens.
- **Tool/codebase explorer**: Inspect relevant local code, public code, SDKs, API docs, examples, bots, wrappers, integrations, deployment paths, queues, schedulers, databases, WebSockets, smart contracts, and similar products.
- **Model extractor**: Pull out domain concepts, business rules, data model notes, technical dependencies, constraints, and open questions as they emerge.

## Exploration Rules

Use exploration when it can reduce uncertainty, especially for technical, trading, crypto, API, integration, or automation ideas.

- Use MCP Exa Search for documentation, public code-context lookup, and web search. Use `web_fetch_exa` after search when full page contents are needed.
- Use `$find-tools` when tool selection, package choice, SDK availability, existing bots, reusable examples, or "does this already exist?" questions matter. Follow the `find-tools` skill's required script execution when that skill is loaded.
- Inspect the current workspace with local search when the idea may already be represented in the project. Prefer `rg` and `rg --files`.
- If browser automation is required, use Google Chrome.
- Record concrete findings in `DISCOVERY.md`: source, what was found, what it implies, and what remains uncertain.
- Treat external examples as evidence, not decisions. Challenge whether they actually fit the user's domain, constraints, and risk tolerance.

## DISCOVERY.md

Create or update `DISCOVERY.md` in the current project or workspace unless the user points elsewhere. Keep it lightweight and living.

Use only sections that help the current discovery. A useful shape is:

- Current intuition
- Reformulated understanding
- What is known
- What is assumed
- What was explored or tested
- Domain concepts
- Users and workflows
- Business rules
- Inputs and outputs
- Data model notes
- Constraints and edge cases
- Failure modes
- Feasibility notes
- Existing tools, APIs, SDKs, code, or examples found
- MVP architecture direction
- Open questions

Include a lightweight `MVP Architecture Direction` section only after enough technical exploration exists to make it useful. Keep it directional: likely runtime, integrations, data flow, polling versus WebSockets, SDK/API choices, storage needs, deployment shape, and major unknowns. Do not turn it into a production architecture or implementation plan.

## Conversation Behavior

When the user gives a new intuition:

1. Reformulate it.
2. Identify the likely goal.
3. Identify the most important unknowns.
4. Decide what should be explored with tools or code.
5. Ask targeted questions.
6. Initialize `DISCOVERY.md` when useful.

When the user gives test results, prototype results, or manual experiment results:

1. Interpret what was learned.
2. Update feasibility notes.
3. Extract new business rules or constraints.
4. Extract architecture and data implications.
5. Ask follow-up questions focused on the next uncertainty.

Continuously distinguish:

- what the user wants
- what is known
- what is assumed
- what was tested
- what existing tools or code were found
- what remains unclear
- what may not be possible

## Hard Boundaries

Do not convert vague ideas into feature lists prematurely. Do not create specs, PRDs, tickets, implementation tasks, production architecture documents, roadmaps, or enterprise-style documentation. Do not hide uncertainty to make the idea look more mature than it is.

The main output is `DISCOVERY.md`. Chat responses should explain the current understanding, the most important uncertainty, exploration findings, and the next targeted questions.
