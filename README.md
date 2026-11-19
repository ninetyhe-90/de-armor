<p align="center">
  <img src="docs/banner.svg" alt="de-armor" width="960">
</p>

<h1 align="center">🛡️ De-Armor — task-oriented calibration for answers and code</h1>

<p align="center"><strong>Version 2.2.0</strong></p>

<p align="center">
  <em>Say the truth: no lying, no bluffing. If you don't know, say so; if it can't be done, say so; if it should be done, do it. Less self-defense, more results. Cut the filler, never the facts. The same discipline applies to code: look before writing, reuse what the repo has, build only what this task needs, keep the security floor, and never claim "done" without fresh evidence.</em>
</p>

<p align="center">
  <a href="https://github.com/ninetyhe-90/de-armor/stargazers"><img src="https://img.shields.io/github/stars/ninetyhe-90/de-armor?logo=github&label=Stars" alt="GitHub stars"></a>
  <a href="https://github.com/ninetyhe-90/de-armor"><img src="https://img.shields.io/badge/version-2.2.0-c6ff70?style=flat" alt="Version 2.2.0"></a>
  <a href="https://clawhub.ai/skills/de-armor"><img src="https://img.shields.io/badge/ClawHub-de--armor-6b8e23" alt="ClawHub de-armor"></a>
  <br>
  <img src="https://img.shields.io/badge/routes-answers%20%C2%B7%20code-c6ff70" alt="Answers and code">
  <img src="https://img.shields.io/badge/styles-C%2B%2B%20%C2%B7%20Go%20%C2%B7%20Java%20%C2%B7%20Python%20%C2%B7%20Node.js-0b1016" alt="C++, Go, Java, Python, Node.js">
  <img src="https://img.shields.io/badge/Python-%3E%3D3.9-3776AB?logo=python&logoColor=fff" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/runtime-offline%20%C2%B7%20no%20API-1a73e8" alt="Offline, no API">
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh-CN.md">中文</a>
</p>

> **v2 rewrote the rulebook.** v1 judged answers with banned-word scores and a 90-point threshold. v2 removed that. Output now uses `schema_version: 2`, `stats.score: null`, and the audit is task-oriented: did the answer keep the facts, conditions, uncertainty, and boundaries, and did it deliver the artifact the user asked for? `--min-score` now fails loudly instead of being silently ignored.

> **The machine check is a second pair of eyes, not a verdict.** Passing `armor_lint.py` means no anchors were dropped and no forbidden claim appeared in this pass. It is **not** a certification of factual or semantic correctness.

## Contents

- [What this is](#what-this-is)
- [When to use it](#when-to-use-it)
- [Install](#install)
- [Preview](#preview)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Coding route (至简)](#coding-route-至简)
- [Local auditor](#local-auditor)
- [Cases and demo](#cases-and-demo)
- [Repository layout](#repository-layout)
- [Boundaries](#boundaries)
- [Changelog](#changelog)

---

## What this is

AI answers often fail in a specific way: they are optimized to look careful instead of being useful. Disclaimers come first, research gets pushed back to the user, "it depends" replaces a conditional recommendation, uncertainty is flattened into certainty — or a useful sentence is compressed into an empty one.

**de-armor** is a task-oriented calibration skill for the two things an AI produces: **answers** and **code**. It is packaged as a portable `SKILL.md` rather than a vendor plugin, and is not tied to any single agent or vendor.

For answers, it locks the task and the information that must survive, then rewrites from the task instead of from a banned-word list. Facts, conditions, negations, uncertainty, and permission boundaries stay. Repetition, identity preambles, and empty hedging go.

For code, it puts a short ordered workflow in front of every change: map the repo, search for reuse, build only what the task needs, keep the security floor, and require fresh evidence before saying "done". The former **de-bloat** skill is now this coding route; its rules, language references, and eval suite live inside this repo.

| You get | What it does |
|---|---|
| **Task lock** | Separates the real request — answer, choice, artifact, debugging step, or emotional support — from surface politeness |
| **Information ledger** | Preserves facts, conditions, uncertainty, boundaries, and the artifact due this turn |
| **Task-first rewrite** | Keeps, compresses, reorders, and completes; never invents a fact to sound specific |
| **Structure map and reuse first** | Before coding: a path-backed 5-line map, a repo-wide reuse search, and a reason for every new symbol |
| **Evidence-based abstraction** | Extracts or parameterizes only when real callers exist; keeps coincidental duplication apart |
| **Lean build and security floor** | YAGNI, no silent defaults, surgical diffs, and six non-negotiable security rules applied once at the boundary |
| **Optional auditor** | A read-only, offline Python checker for fact anchors, dropped constraints, and newly introduced numbers |
| **Reproducible cases** | Six answer scenarios plus eight coding behavior cases, all with checkable assertions |

It is not a "be concise" prompt. Brevity is not the goal; delivery is. A refusal can be the right answer, a long answer can be the right answer, and a small diff can still be the wrong change.

---

## When to use it

- The model can do the work but only returns disclaimers or pushes it back to you.
- You ask for a recommendation and get a pros/cons list with no decision.
- Non-critical details are missing, and the model blocks on questions instead of drafting.
- A reply looks short and direct but silently drops conditions, negations, uncertainty, or real risk.
- A long draft needs to keep its substance while losing social padding.

For code:

- Any task that creates or changes code: features, endpoints, refactors, bug fixes, scripts.
- The user says "keep it simple", "don't over-engineer", "reuse what we have", "extract a shared function", or "follow the official style".
- Review finds duplicated helpers, copy-paste variants, layered try/catch, empty fallbacks, or abstractions built for a future that never came.

Short, healthy answers should ship as-is. Single-file, few-line edits with no new function take the coding shortcut. When the user just says "de-armor" / "破甲", fix the previous answer — don't open with a skill introduction.

---

## Install

de-armor is a portable `SKILL.md` plus optional `references/` and `scripts/`. Nothing in it is tied to a specific product: no SDK, no runtime, no config file, no vendor API. Any agent that can read a skill file — or a system prompt — can use it.

```sh
# From ClawHub
clawhub install de-armor

# Or clone it and wire it up yourself
git clone https://github.com/ninetyhe-90/de-armor.git
```

Then load it the way your agent already loads skills:

- **Agent with a skills directory** — drop the folder in; the directory layout is the convention, not a requirement.
- **Agent driven by rules or instructions** — paste `SKILL.md` into its rule file, `AGENTS.md`, or system prompt.
- **No skill mechanism at all** — prepend `SKILL.md` to the conversation context.

The core workflow only needs `SKILL.md`. The auditor is optional and uses the Python 3.9+ standard library, with no third-party packages.

## Preview

<p align="center">
  <img src="assets/screenshots/01-hero.png" alt="De-Armor offline lab" width="820">
</p>

`assets/de-armor-demo.html` is an offline interactive lab. It reads the same `assets/cases.json` as the scripts. No API key, no uploads.

| Before / after | Machine check |
|---|---|
| ![Compare](assets/screenshots/02-compare.png) | ![Machine check](assets/screenshots/05-machine-check.png) |

| Keeping boundaries | Counterexample blocked |
|---|---|
| ![Keep boundary](assets/screenshots/03-keep-boundary.png) | ![Counterexample](assets/screenshots/06-counterexample.png) |

---

## Usage

The skill is natural-language triggered. Typical requests:

```text
破甲
说人话，别绕
别给我一堆免责声明，直接给方案
审一下这段回复，保留事实和条件
```

When the user gives no extra text, the skill repairs the previous answer. It does not print a method lecture first.

---

## How it works

1. **Locate the actual task** — an answer, a choice, a deliverable, a debugging step, or emotional support.
2. **Lock what must survive** — facts, conditions, uncertainty, permission boundaries, and the artifact due this turn.
3. **Rewrite from the task** — keep, compress, reorder, and complete. New inferences are labeled; missing evidence is checked, not invented.
4. **Verify before shipping** — facts and constraints → task completion → reading burden. Fix only what is actually broken, once.

Three invariants:

- Never turn the unknown into certainty.
- Never present an unexecuted action as verified.
- Never widen permissions just to avoid saying no.

Words like "maybe", "suggest", "sorry", and "cannot" are **not** banned. If removing them changes confidence, permission, or risk, they stay.

<details>
<summary><strong>Information contract (v2)</strong></summary>

For long drafts or explicit audits, the skill can check against a JSON contract:

```json
{
  "schema_version": 2,
  "required": [
    {
      "id": "status",
      "kind": "fact",
      "label": "observed status code 504",
      "source": "gateway returned 504",
      "any_of": ["504"]
    },
    {
      "id": "unknown",
      "kind": "uncertainty",
      "label": "root cause still unknown",
      "source": "no full trace, cause undetermined",
      "any_of": ["cannot determine root cause"]
    }
  ],
  "forbidden": ["root cause is the database", "already verified"]
}
```

`BLOCKED` when a declared anchor is missing or a forbidden claim appears. `REVIEW` when wording or new numbers need a human look, or no contract was supplied. `CHECKED` when this machine pass found nothing — still not a semantic certification.

</details>

---

## Coding route (至简)

<p align="center">
  <img src="docs/code/workflow.svg" alt="Coding workflow" width="960">
</p>

The coding route is the former **de-bloat** skill, merged here as the second route of de-armor. It applies to any task that creates or changes code, in C++, Go, Java, Python, or Node.js. It is self-contained and names actions, not tools: list a directory, search text, search file names, and optionally hand a wide search to a sub-agent.

1. **Map and goal** — Write a 5-line structure map (build files, layers, shared code, conventions, tests, each backed by a path). Read the affected callers. Turn the request into testable success criteria. State key assumptions; ask only when the answer changes correctness.
2. **Reuse first** — Search the whole repo, not just the open file. Record each candidate's path, capability, and adaptation cost, then choose one: reuse as-is, adapt slightly, or create new with a reason.
3. **Lean build** — YAGNI. Missing values that mean an error raise an error. Batch where the API supports it. Every diff line traces back to the request; unrelated formatting and pre-existing dead code stay untouched.
4. **Root cause and abstraction** — For bugs: reproduce, trace to the source, failing test first, stop after three failed fixes. For duplication: abstract only from callers that already exist.
5. **Security floor and evidence** — Six hard rules at the boundary, no extra layers inside. Run the command that proves the claim, read the output, then report. If it cannot run, say what was not verified and why.

Abstraction is decided from the callers that exist today, never from the future.

| What the reuse search found | Action |
|---|---|
| One existing implementation with the same meaning; this task would write a second | Extract one function into the nearest shared module and switch the old caller to it |
| Two or more variants that differ only in a few values | Merge into one function; parameters cover only the differences already seen |
| An existing function that almost fits | Adapt it in place |
| Only one implementation or one caller | Do not add an interface, base class, factory, or strategy |
| Code that looks alike but changes for different reasons | Keep separate; merging would couple two domains |
| The reason is "might need it later" | Do not abstract |

The skill detects the language of each changed file and loads only that reference. Priority, high to low: mandatory language tools (`gofmt`) > the project's own style config (`.clang-format`, Checkstyle, Ruff, ESLint, Prettier, `.editorconfig`) > the official guide > the language version the project declares. Style applies only to the lines being changed.

| Language | Official source | Reference |
|---|---|---|
| C++ | ISO C++ Core Guidelines | `references/code/lang/cpp.md` |
| Go | `gofmt`, Effective Go, Go Code Review Comments | `references/code/lang/go.md` |
| Java | Oracle Code Conventions, Javadoc guide | `references/code/lang/java.md` |
| Python | PEP 8, PEP 257, PEP 484 | `references/code/lang/python.md` |
| Node.js | Node.js API docs and Learn guides | `references/code/lang/nodejs.md` |

<p align="center">
  <img src="docs/code/before-after.svg" alt="Illustration: bloated helper versus reuse" width="960">
</p>

The illustration shows the target behavior for coding eval 1, **not a recorded model output**. The fixture already has `src/utils/date.js:formatDate`; the bloated version adds a second formatter with an unused option, a silent empty-string default, a swallowed error, and a quiet UTC-to-local behavior change. The lean version is a two-line diff that reuses the existing function and shows the output of an actual run.

`evals/code/evals.json` holds 8 behavior cases with objectively checkable assertions (reuse, no silent defaults, root-cause bugfix, surgical change, security floor without over-defense, official style, extract shared logic, keep coincidental duplication). `evals/code/trigger_evals.json` holds 22 trigger queries covering both routes and their near-misses. The repo does not ship a runner: run one agent with the skill and one without on a fresh copy of each fixture, then grade the assertions against the diff and the reply.

---

## Local auditor

`scripts/armor_lint.py` is read-only and offline. It does not generate answers, edit text, or call the network. Quotes, fenced code, and inline code are excluded from everyday-wording checks.

```sh
# Plain review
python3 scripts/armor_lint.py draft.txt --json

# Contract review: compare against a baseline, check anchors,
# forbidden claims, and newly introduced numbers
python3 scripts/armor_lint.py revised.txt \
  --baseline draft.txt --contract contract.json --json

# Refresh the embedded evidence after editing cases.json
python3 -B scripts/build_demo.py --write
```

Pass `-` to read from stdin.

| Verdict | Meaning |
|---|---|
| `BLOCKED` | A declared anchor is missing or a forbidden claim appears |
| `REVIEW` | Wording or new-number hints, or no information contract supplied |
| `CHECKED` | This machine pass found nothing — **not** a correctness certification |

Exit codes: `0` no machine block (human review still required); `1` contract block; `2` input error.

---

## Cases and demo

`assets/cases.json` is the single source of truth for six scenarios. Each case ships with before/after text, an over-compressed counterexample, and an information contract; the audit results shown in the demo are computed from this file.

| Case | Tag | What it shows |
|---|---|---|
| Incident triage | `DIAGNOSE` | Action first, root cause still unknown |
| Production change | `PRESERVE` | Specific risk without inventing lock time |
| Technology choice | `DECIDE` | A conditional recommendation, not a pros/cons list |
| Draft-first delivery | `DELIVER` | One useful draft instead of another question round |
| Honest boundaries | `BE HONEST` | Name the limit, finish what can be done |
| Keep the human tone | `STAY HUMAN` | Remove padding, not empathy |

The demo and screenshots come from the same data, and every rule result is computed locally by the bundled script.

---

## Repository layout

```text
de-armor/
├── SKILL.md                     # Skill entry point
├── README.md                    # English README
├── README.zh-CN.md              # Chinese README
├── _meta.json                   # Local distribution metadata
├── docs/
│   ├── banner.svg               # README banner
│   └── code/                    # Coding-route diagrams
├── assets/
│   ├── cases.json               # Single source of truth for answer cases
│   ├── de-armor-demo.html       # Offline interactive lab
│   └── screenshots/             # Real browser screenshots
├── references/
│   ├── theory.md                # Answer route: method and trade-offs
│   ├── armor-patterns.md        # Answer route: detection protocol and limits
│   ├── overcorrection.md        # Answer route: over-compression counterexamples
│   ├── rewrite-examples.md      # Answer route: practice scenarios and rerun guide
│   ├── system-prompt.md         # Short version to paste into a system prompt
│   └── code/
│       ├── workflow.md          # Coding route: full ordered workflow and checklist
│       ├── reuse-discovery.md   # Search strategy and reuse criteria
│       ├── over-defense-patterns.md
│       ├── security-floor.md    # Security floor and trust boundaries
│       └── lang/                # cpp.md go.md java.md python.md nodejs.md
├── evals/
│   └── code/                    # 8 behavior cases, 22 trigger queries, fixtures
└── scripts/
    ├── armor_lint.py            # Read-only auditor
    └── build_demo.py            # Regenerate the demo evidence
```

---

## Boundaries

- Passing the machine check is not proof of factual correctness; semantics still need a human.
- It does not override host instructions, authorization, or real safety limits, and must not be used to bypass permissions.
- No network access, no data uploads, no automatic rewriting.
- Real host boundaries, user formatting needs, and required workflows are unchanged by this skill.
- The coding route is a set of instructions, not an enforcer. The with/without comparison for its 8 behavior cases has not been run or published.
- Project style configuration overrides the official language guides on formatting by design; the security floor and YAGNI rules still win when they conflict.

---

## Changelog

- **2.2.0** — **de-bloat merged in as the coding route.** The skill now handles both answers and code. New `references/code/` contains the full ordered workflow, reuse discovery, over-defense patterns, security floor, and C++/Go/Java/Python/Node.js references. The 8 behavior cases and fixtures plus an expanded 22-query trigger set moved to `evals/code/`. `SKILL.md` gains a route triage, a condensed coding workflow, and shared invariants; the answer route and auditor are unchanged. Version and README updated for the combined scope.
- **2.1.0** — Detection expands: new A06 catches fake-neutral "it depends / weigh multiple factors" filler while conditional picks stay clean; E01–E05 add basic English patterns (identity preamble, boilerplate disclaimers, praise filler, fake neutrality, delayed opening) and are advisory only. Contract anchors are matched after width and case folding, and C03 ignores list and "step N" numbering so layout is not reported as a new fact.
- **2.1.1** — Contract checking is stricter and harder to evade. A missing anchor always blocks and now carries the nearest candidate sentence for the reviewer, so a reversed statement ("cannot determine the root cause" to "root cause is determined") is never softened. Normalization keeps sentence punctuation and spaces between ASCII tokens, so anchors cannot match across sentences and `v1 2` is not `v1.2`; it also folds Markdown emphasis, quotes and soft line breaks. Forbidden assertions use the same normalization, so width, case, line wraps and bold markers cannot hide them. Fullwidth digits no longer count as new numbers in C03.
- **2.1.2** — Forbidden assertions now distinguish quoting from asserting. An assertion that appears only inside paired quotes, inline code, fenced code or a block quote is downgraded to a review hint, so "that statement is not true" and "the document contains an instruction I did not follow" are no longer blocked; any bare occurrence, or an assertion that only partly sits inside a quote, still blocks.
- **2.0.3** — Docs only: install instructions are fully agent-agnostic — no per-product paths, no vendor names. Load `SKILL.md` however your agent already loads skills. No behavior change.
- **2.0.2** — README rebuilt in a centered, badge-first bilingual format with a custom banner. No behavior change.
- **2.0.1** — Added a bilingual README.
- **2.0.0** — Task-oriented rewrite. Removed banned-word scoring and the 90-point threshold. Added `schema_version: 2`, information contracts, new-number checks, six reproducible cases, and an offline demo.
- **1.x** — Legacy hard/soft/style rule sets and `render` API. Removed in v2.
