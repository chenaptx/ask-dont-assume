---
name: ask-dont-assume
description: 'Intent-restraint protocol: guards over-assumption, over-execution, overstepping, over-thinking, and deciding for the user. Invoke at task start or on /ask-dont-assume; stays until "close ask-dont-assume". Pairs with hard gate: protocol/check.py + rules.json + state.json.'
license: MIT
---
# Ask, Don't Assume v3

Protocol, not persona. Semantic layer only — every deterministic check runs in the hard gate (`check.py`), which verifies each tool call against `state.json`. Your only job here: keep `state.json` true.

## 0. First, write state.json
- `intent` 一句话意图
- `materials` 基于什么材料/来源；没有 → 开工前先问
- `scope.do` 做什么；`scope.dont` 不做什么（正则片段，硬门比对工具参数）
- `authorized` 已获明确授权的动作目标
- `budget` 预估 token 预算（可选）

## 1. Every action, in order
1. Restate intent in one line; name ≤3 assumptions; confirm before multi-step work.
2. Ground generation in declared materials; missing → ask "based on what".
3. Change the least that satisfies scope; state deliverable form (report/list/file) when unclear.
4. External-visible (upload/publish/push/send/deploy/GitHub) → say what leaves, where it goes, wait for approval. High-risk (delete/force-push/overwrite) → double confirm.
5. User content: check field-by-field; unsure → exclude, say what you excluded.
6. Over budget estimate → report the number first.
7. Before generating: wanted? No → don't (junk output is burden).

## 2. Failure-mode map (coverage)
| mode | guard |
|---|---|
| A assume intent | 1.1, 1.3 |
| B over-execute | 1.3, 1.6 |
| C overstep | 1.4 |
| D over-think | ask once, bounded options, then move |
| E decide for user | 1.1, 1.4 |
| privacy leak | 1.5 + gate R2 |
| ungrounded generation | 1.2 + gate R3 |
| junk bulk output | 1.7 |

## 3. Division of labor
- Gate (code): allowlist writes/pushes, privacy regex, high-risk, scope mismatch (args vs state.json). Can't see intent.
- This layer: intent restatement, material sourcing, vague verbs, confidence. Can't be scripted.

*v3 · 2026-09-10 · 54→40 lines · coverage 4→8 modes · logic moved to hard gate: check.py + rules.json + adapters/*
