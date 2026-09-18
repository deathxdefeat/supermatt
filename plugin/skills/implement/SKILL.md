---
name: implement
description: Implement a spec, a ticket, or a concrete behaviour test-first (red-green), then commit and review. Use when the user wants something built from a spec or tickets, wants to build test-first, mentions "red-green-refactor", or wants integration tests.
argument-hint: "[ticket path, number or URL]"
---

# Implement

Build the work described by the spec or ticket the user passes (or the behaviour they describe) test-first, commit it, then review it.

## Process

1. **Restate** in two or three lines what the spec or ticket asks for and which seams you will test. If it contradicts the code, the spec, or an ADR, say so and stop; otherwise continue without waiting.
2. **Record the fixed point**: `git rev-parse HEAD`. Review diffs against it.
3. **Track it** when this repo is set up for supermatt (`"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" status` says so) and a feature is active: `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" ticket <NN> implementing`. If it refuses because an earlier ticket is still unreviewed, run `/supermatt:review` on that ticket first. Code edits outside a ticket in progress may be blocked by the `ticket_before_code` rule.
4. **Build it test-first** with the loop below, at the pre-agreed seams. Run the typechecker (if the project has one) and single test files regularly, and the full test suite once at the end.
5. **Commit** to the current branch. When the `tests_before_commit` rule is on, the commit runs the configured test command first and a red suite blocks it: fix the code, not the rule.
6. **Mark it for review**: `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" ticket <NN> needs-review` (when tracked), then call the Skill tool with "supermatt:review", passing the fixed point from step 2.

## Test-driven development

TDD is the red → green loop. This section is the reference that makes that loop produce tests worth keeping: what a good test is, where tests go, the anti-patterns, and the rules of the loop. Every section applies on every cycle: consult them before and during the loop, not after.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

### What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

### Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user (a spec or ticket that names its seams counts as confirmed). No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front is how testing effort lands on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), read `${CLAUDE_PLUGIN_ROOT}/skills/architecture/DESIGN.md` for the vocabulary. It is the shared source of the module, interface, depth, seam, adapter, leverage and locality terms, and it is a reference to consult, not a session to run.

### Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

### Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (see the `supermatt:review` skill), not the red → green implementation cycle.
