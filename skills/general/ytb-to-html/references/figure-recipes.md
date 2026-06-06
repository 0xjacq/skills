# Figure Recipes

Use these patterns for structured transcript content.

## Timeline with many milestones

Best for:
- release histories
- model/version arcs
- event sequences with dates or labels

Preferred pattern:
- stacked HTML milestone cards
- or a simple table with columns such as `phase`, `what changed`, and
  `why it matters`

Use SVG only when:
- there are few milestones
- each label is short
- the visual spacing is obviously safe

## Step flow or loop

Best for:
- initializer loops
- evaluation cycles
- repeated agent workflows

Preferred pattern:
- ordered list with bold step names
- or a responsive grid of step cards
- or a simple block SVG with one short label per block and the details
  outside the blocks

Avoid:
- pseudo-code diagrams with many long arrow lines
- trying to fit the full loop explanation into one `pre` block

## Comparison or tradeoff

Best for:
- model vs harness
- generator vs evaluator
- greenfield vs brownfield

Preferred pattern:
- HTML table
- paired callouts
- short two-column card grid

## Support figure with caption

Best for:
- concept reinforcement beside prose
- a simple visual summary of a section

Preferred pattern:
- one calm figure
- one short caption explaining what it teaches
- one provenance line when the figure is generated or interpretive

## Figure selection rule

Pick the least fragile pattern that still teaches the idea:
1. prose or list
2. table or cards
3. responsive SVG
4. optional support image beside the exact HTML/SVG explanation
