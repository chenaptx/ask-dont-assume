#!/usr/bin/env python3
"""L3 verdict gate (pure if-else, no LLM): 6 enum cells -> verdict JSON.

Input : {"action_kind","target_kind","sensitivity","in_scope","cost_tier","output_kind"}
Output: {"verdict","risk_dimension","risk_level"}
Rules table mirrors protocol/contract.md; first match wins, top-down.
"""
import json
import sys

RULES = [
    # (name, condition, verdict, dimension, level)
    ("r1_emit_unauth",      lambda c: (c["action_kind"] == "emit" or c["target_kind"] == "external_service") and c["sensitivity"] != "authorized", "deny", "privacy", "high"),
    ("r2_secret_unauth",    lambda c: c["target_kind"] == "secret_dir" and c["sensitivity"] != "authorized", "deny", "privacy", "high"),
    ("r3_cred_nonlocal",    lambda c: c["sensitivity"] == "credential" and c["target_kind"] != "local_file", "deny", "privacy", "high"),
    ("r4_cred_remoteemit",  lambda c: c["sensitivity"] == "credential" and c["output_kind"] == "remote_emit", "deny", "privacy", "high"),
    ("r5_git_outscope",     lambda c: c["target_kind"] == "git" and not c["in_scope"], "deny", "privacy", "high"),
    ("r6_remoteemit_cred",  lambda c: c["output_kind"] == "remote_emit" and c["sensitivity"] == "credential", "deny", "privacy", "high"),
    ("r7_private_outscope", lambda c: not c["in_scope"] and c["sensitivity"] == "private", "deny", "privacy", "med"),
    ("r8_ext_outscope",     lambda c: c["cost_tier"] == "ext" and not c["in_scope"], "degrade", "token", "high"),
    ("r9_ext_authorized",   lambda c: c["cost_tier"] == "ext" and c["sensitivity"] == "authorized", "degrade", "token", "med"),
    ("r10_high_remoteemit", lambda c: c["cost_tier"] == "high" and c["output_kind"] == "remote_emit", "degrade", "token", "med"),
    ("r11_remote_high",     lambda c: c["target_kind"] == "remote" and c["cost_tier"] == "high", "degrade", "time", "med"),
    ("r12_msg_private",     lambda c: c["output_kind"] == "sent_message" and c["sensitivity"] == "private", "degrade", "privacy", "med"),
    ("r13_allow_local",     lambda c: c["in_scope"] and c["sensitivity"] == "authorized" and c["target_kind"] == "local_file", "allow", "none", "low"),
    ("r14_allow_local_cheap", lambda c: c["target_kind"] == "local_file" and c["in_scope"] and c["cost_tier"] != "ext", "allow", "none", "low"),
]

ALLOWED = {
    "action_kind": {"read", "write", "execute", "network", "emit", "spawn"},
    "target_kind": {"local_file", "secret_dir", "git", "remote", "external_service", "api"},
    "sensitivity": {"authorized", "private", "credential", "none"},
    "in_scope": {True, False},
    "cost_tier": {"low", "med", "high", "ext"},
    "output_kind": {"none", "local_file", "remote_emit", "sent_message"},
}


def verdict(cells):
    for name, cond, v, dim, lvl in RULES:
        if cond(cells):
            return {"verdict": v, "risk_dimension": dim, "risk_level": lvl, "rule": name}
    return {"verdict": "allow", "risk_dimension": "none", "risk_level": "low", "rule": "default"}


def main():
    raw = sys.argv[sys.argv.index("--cells") + 1] if "--cells" in sys.argv else None
    if not raw:
        cells = json.load(sys.stdin)
    else:
        cells = json.loads(raw)
    for k, allowed in ALLOWED.items():
        if k not in cells or cells[k] not in allowed:
            print(json.dumps({"error": f"invalid cell {k}: {cells.get(k)!r}"}))
            sys.exit(2)
    print(json.dumps(verdict(cells)))


if __name__ == "__main__":
    main()
