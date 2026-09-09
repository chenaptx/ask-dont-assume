# Ask, Don't Assume

> **Don't decide for me.**

The **intent-guard protocol** for AI coding agents. Stop the over-assumption, stop the overreach, stop the overwork — make your agent **ask first, never assume**.

**Status: 🚧 Protocol in development · name claimed 2026-09-10**

---

## The problem

Your agent doesn't overdo because it's eager. It overdoes because it **assumes** — it fills in the intent you never stated, expands the scope you never drew, and executes the decision you never made.

Research-backed mechanism chain:

`next-token prediction` → arbitrary completion of missing parameters → RLHF rewards "helpful" over "honest" → *premature direct response* → **scope creep / goal expansion**

Measured: AgentLens benchmark — 15/32 agent reviews show unstable scope control. SSTA-32 — 41.7% over-commitment in default execution.

## The protocol (5 steps)

1. **Intent declaration** — restate the understood intent + disclose every assumption
2. **Scope lock** — declare boundaries: what will change / what will not
3. **Ask first** — hit ambiguity → ask with bounded options, never guess
4. **Minimal execution** — YAGNI ladder + token budget
5. **Post-action review** — diff vs declared scope → revert / report

## Enforcement layers

| Layer | Mechanism | Coverage |
|---|---|---|
| L1 Protocol | SKILL.md / AGENTS.md | 30+ platforms |
| L2 Hard gate | Platform hooks (PreToolUse deny) | Claude Code / Cursor / Codex / TRAE |
| L3 Fallback | Middleware / human-in-the-loop | optional, enterprise |

## Manifesto

Ask first. Don't assume. Don't decide for me. Stop overreaching. Stop overworking.

`#AskDontAssume` `#DontDecideForMe` `#StopOverreaching`

## Roadmap

- [ ] Protocol skill (SKILL.md) — the universal intent-declaration layer
- [ ] Hook configs (PreToolUse scope validation)
- [ ] "Cost of not asking" benchmark (the missing measurement)
- [ ] Website — askdontassume.ai
