#!/usr/bin/env python3
"""Hard gate: decide allow/deny/ask for a tool call against state.json + rules.json.

Platform-neutral. Adapters (Claude Code hooks, harness wrappers) call:
    check.py --tool TOOL --input JSON --state PATH
returns {"decision": "allow|deny|ask", "reason": "..."} — same shape Claude Code PreToolUse expects.
"""
import json
import os
import re
import sys


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def hits(patterns, text):
    return next((p for p in patterns if re.search(p, text, re.I)), None)


def decide(state, rules, tool, args):
    blob = json.dumps(args)
    # R2 privacy: deny first, always
    if p := hits(rules["privacy"], blob):
        return {"decision": "deny", "reason": f"privacy:{p}"}
    # R1 authorized: explicit allow beats everything except privacy
    if hits(rules["allow"], blob):
        return {"decision": "allow", "reason": "authorized"}
    # R3 facts: generation needs declared materials
    if tool in rules["generate_tools"] and not state.get("materials"):
        return {"decision": "ask", "reason": "materials"}
    # R4 scope: tool args vs declared scope.dont
    scope = state.get("scope", {})
    if tool in rules["scope_tools"] and scope.get("dont") and hits(scope["dont"], blob):
        return {"decision": "ask", "reason": "out_of_scope"}
    # R5 high-risk: double confirm
    if tool in rules["high_risk"] or hits(rules["high_risk_patterns"], blob):
        return {"decision": "ask", "reason": "high_risk"}
    # R6 budget
    budget = state.get("budget")
    if budget and len(blob) + len(tool) > budget / 2000:
        return {"decision": "ask", "reason": "budget"}
    return {"decision": "allow", "reason": ""}


def main():
    argv = sys.argv[1:]

    def flag(name):
        return argv[argv.index(name) + 1] if name in argv else None

    tool = flag("--tool") or ""
    raw = flag("--input") or "{}"
    state_path = flag("--state") or os.environ.get("CHECK_STATE", "state.json")
    rules_path = os.environ.get("CHECK_RULES", os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules.json"))
    state = load_json(state_path, {})
    rules = load_json(rules_path, {})
    args = load_json(raw, {}) if raw.startswith(("{", "[")) else {}
    print(json.dumps(decide(state, rules, tool, args)))


if __name__ == "__main__":
    main()
