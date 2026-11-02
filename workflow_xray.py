"""X-ray a campaign workflow before it runs: dead ends, missing error branches, unbounded queries.

Reads a simplified workflow XML (activities + transitions, see examples/), builds the graph
and reports structural risks with a 0-100 health score and a Mermaid diagram.
The XML format here is a teaching simplification, not Adobe Campaign's package export.
Standard library only.
"""
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, deque

RISKY = {"query", "delivery", "script"}


def load(path):
    root = ET.parse(path).getroot()
    acts = {a.get("id"): dict(a.attrib) for a in root.findall("activity")}
    edges = [dict(t.attrib) for t in root.findall("transition")]
    return root.get("name"), acts, edges


def analyse(acts, edges):
    out, kinds = defaultdict(list), defaultdict(set)
    for e in edges:
        out[e["from"]].append(e["to"])
        kinds[e["from"]].add(e.get("kind", "ok"))
    findings = []

    def add(level, aid, msg):
        findings.append((level, aid, msg))

    starts = [a for a, v in acts.items() if v["type"] == "start"]
    if not starts:
        add("error", "-", "no start activity")
    if not any(v["type"] == "end" for v in acts.values()):
        add("error", "-", "no end activity")

    seen = set()
    queue = deque(starts)
    while queue:
        a = queue.popleft()
        if a in seen:
            continue
        seen.add(a)
        queue.extend(out[a])
    for a in acts:
        if a not in seen and starts:
            add("warning", a, "unreachable from start (dead code)")

    for a, v in acts.items():
        t = v["type"]
        if t != "end" and not out[a]:
            add("error", a, "dead end: no outgoing transition, the run just stops")
        if t in RISKY and "error" not in kinds[a]:
            add("error", a, f"{t} has no error branch: a failure alerts nobody")
        if t == "query" and not v.get("filter"):
            add("error", a, "query has no filter: full recipient table scan")
        if t == "query" and not v.get("limit"):
            add("warning", a, "query has no limit")
        if t == "fork":
            joins_reached = set()
            for branch in out[a]:
                q, s2 = deque([branch]), set()
                while q:
                    x = q.popleft()
                    if x in s2:
                        continue
                    s2.add(x)
                    if acts.get(x, {}).get("type") == "join":
                        joins_reached.add(x)
                        continue
                    q.extend(out[x])
                if not joins_reached & s2:
                    add("warning", a, f"fork branch via '{branch}' never reaches a join")
    return findings


def health(findings):
    return max(0, 100 - sum(15 if lvl == "error" else 5 for lvl, _, _ in findings))


def mermaid(acts, edges):
    lines = ["flowchart LR"]
    for a, v in acts.items():
        lines.append(f'  {a}["{v.get("label", a)}"]')
    for e in edges:
        arrow = "-.->|error|" if e.get("kind") == "error" else "-->"
        lines.append(f"  {e['from']} {arrow} {e['to']}")
    return "\n".join(lines)


def main(path, show_diagram=False):
    name, acts, edges = load(path)
    f = analyse(acts, edges)
    print(f"{name}: health {health(f)}/100, {len(acts)} activities")
    for lvl, aid, msg in sorted(f, key=lambda x: (x[0] != "error", x[1])):
        print(f"  {lvl:<7} {aid:<14} {msg}")
    if show_diagram:
        print("\n```mermaid\n" + mermaid(acts, edges) + "\n```")
    return 1 if any(l == "error" for l, _, _ in f) else 0


if __name__ == "__main__":
    args = sys.argv[1:] or ["examples/newsletter_broken.xml"]
    sys.exit(main(args[0], "--diagram" in args))
