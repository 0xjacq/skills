# Artifact Modes

Choose one dominant mode before writing.

## `onboarding`

Use when the reader is new to the project.

Focus on:
- project purpose
- high-level architecture
- key files and directories
- how to run or use it
- glossary
- suggested next reading

Default structure:
1. What this project is
2. Why it exists
3. System map
4. Key files
5. How to run or use it
6. Risks and open questions
7. Read next

## `architecture`

Use when the reader needs internal structure.

Focus on:
- modules
- boundaries
- flows
- dependencies
- invariants
- data contracts

Default structure:
1. System overview
2. Main components
3. Data or control flow
4. Integration points
5. Key invariants
6. Failure modes
7. Read next

## `usage`

Use when the reader mainly needs operational understanding.

Focus on:
- install or run steps
- configuration
- entry points
- common workflows
- caveats

Default structure:
1. What it does
2. Prerequisites
3. Setup
4. Common commands or flows
5. Config surface
6. Known pitfalls

## `code-explainer`

Use when one subsystem needs explanation.

Focus on:
- one core flow
- 3 to 5 annotated snippets
- terminology
- gotchas

Default structure:
1. What this subsystem does
2. Flow diagram
3. Important code excerpts
4. Invariants and gotchas
5. Read next

## `change-brief`

Use when summarizing agent or branch work.

Focus on:
- what changed
- why it changed
- behavior impact
- review hotspots
- unresolved risks

Default structure:
1. Change summary
2. Affected areas
3. Before and after
4. Review hotspots
5. Risks and follow-up

## `research-brief`

Use when synthesizing findings, options, or hypotheses.

Focus on:
- findings
- evidence
- assumptions
- tradeoffs
- next validation steps

Default structure:
1. Question
2. Findings
3. Comparison
4. Assumptions
5. Risks
6. Next steps
