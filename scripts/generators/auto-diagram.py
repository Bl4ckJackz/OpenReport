#!/usr/bin/env python3
"""auto-diagram.py — converte descrizioni testuali in diagrammi Mermaid/PlantUML.

Supporta 5 tipi di diagramma:

1. **flowchart** — da testo narrativo che descrive un flusso
2. **sequence** — da dialogo/interazione attori
3. **class** — da descrizione struttura entità
4. **state** — da descrizione stati/transizioni
5. **gantt** — da lista milestone con date

Input: descrizione naturale in un file .txt o stdin, con hint strutturati:
    TYPE: flowchart
    TITLE: Login Flow
    NODES:
      A[User clicks login]
      B[Enter credentials]
      C{Credentials valid?}
      D[Dashboard]
      E[Error message]
    EDGES:
      A --> B
      B --> C
      C -->|yes| D
      C -->|no| E

Oppure più libero (auto-parse):
    # Flowchart: User registration
    Start: user opens app
    then: enter email
    decision: email valido?
      if yes: send confirmation
      if no: show error
    end

Output: blocco ```mermaid``` o ```plantuml``` pronto da incollare nel doc.

Usage:
    auto-diagram.py <input.txt> [--engine mermaid|plantuml] [--type TYPE] [-o out.md]
    auto-diagram.py --template flowchart > skeleton.txt    # mostra template
"""
import argparse
import pathlib
import re
import sys


TEMPLATES = {
    "flowchart": """TYPE: flowchart
TITLE: Titolo del flusso
NODES:
  A[Inizio]
  B[Azione 1]
  C{Decisione?}
  D[Azione 2]
  E[Fine]
EDGES:
  A --> B
  B --> C
  C -->|si| D
  C -->|no| E
  D --> E
""",
    "sequence": """TYPE: sequence
TITLE: Titolo sequenza
ACTORS:
  - User
  - Frontend
  - Backend
  - DB
MESSAGES:
  User->>Frontend: login(email, password)
  Frontend->>Backend: POST /auth
  Backend->>DB: SELECT user
  DB-->>Backend: user row
  Backend-->>Frontend: JWT token
  Frontend-->>User: redirect dashboard
""",
    "class": """TYPE: class
TITLE: Modello dati
CLASSES:
  User:
    - id: UUID
    - email: string
    - password_hash: string
    + login(email, password): bool
    + logout(): void
  Order:
    - id: UUID
    - user_id: UUID
    - total: decimal
    + calculateTotal(): decimal
RELATIONS:
  User ||--o{ Order : places
""",
    "state": """TYPE: state
TITLE: Ciclo stati Documento
STATES:
  - draft
  - in-review
  - approved
  - archived
TRANSITIONS:
  draft --> in-review : submit
  in-review --> approved : approve
  in-review --> draft : request_changes
  approved --> archived : archive_after_1y
""",
    "gantt": """TYPE: gantt
TITLE: Roadmap Q2 2026
SECTIONS:
  - Fase 1:
      - Analisi: 2026-04-01, 10d
      - Design: after Analisi, 7d
  - Fase 2:
      - Sviluppo: after Design, 20d
      - Testing: after Sviluppo, 10d
""",
}


def parse_structured(text):
    """Parse strutturato hint-based (TYPE/TITLE/NODES ecc.)."""
    sections = {}
    current = None
    current_lines = []
    for line in text.split("\n"):
        m = re.match(r"^([A-Z_]+):\s*(.*)$", line)
        if m:
            if current:
                sections[current] = "\n".join(current_lines).strip()
            current = m.group(1)
            inline = m.group(2).strip()
            current_lines = [inline] if inline else []
        elif current:
            current_lines.append(line)
    if current:
        sections[current] = "\n".join(current_lines).strip()
    return sections


def render_flowchart_mermaid(sections):
    out = ["```mermaid", "flowchart TD"]
    if sections.get("TITLE"):
        out.append(f"    %% {sections['TITLE']}")
    for n in sections.get("NODES", "").split("\n"):
        n = n.strip()
        if n:
            out.append(f"    {n}")
    for e in sections.get("EDGES", "").split("\n"):
        e = e.strip()
        if e:
            out.append(f"    {e}")
    out.append("```")
    return "\n".join(out)


def render_flowchart_plantuml(sections):
    out = ["```plantuml", "@startuml"]
    if sections.get("TITLE"):
        out.append(f"title {sections['TITLE']}")
    out.append("start")
    for n in sections.get("NODES", "").split("\n"):
        n = re.sub(r"^\w+\[|\]$", "", n.strip())
        if n:
            out.append(f":{n};")
    out.append("stop")
    out.append("@enduml")
    out.append("```")
    return "\n".join(out)


def render_sequence_mermaid(sections):
    out = ["```mermaid", "sequenceDiagram"]
    if sections.get("TITLE"):
        out.append(f"    %% {sections['TITLE']}")
    for a in sections.get("ACTORS", "").split("\n"):
        a = a.strip().lstrip("-").strip()
        if a:
            out.append(f"    participant {a}")
    for msg in sections.get("MESSAGES", "").split("\n"):
        msg = msg.strip()
        if msg:
            out.append(f"    {msg}")
    out.append("```")
    return "\n".join(out)


def render_class_mermaid(sections):
    out = ["```mermaid", "classDiagram"]
    if sections.get("TITLE"):
        out.append(f"    %% {sections['TITLE']}")
    classes_block = sections.get("CLASSES", "")
    current_class = None
    for line in classes_block.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.endswith(":") and not stripped.startswith(("-", "+")):
            current_class = stripped.rstrip(":").strip()
            out.append(f"    class {current_class} {{")
        elif stripped.startswith("-") or stripped.startswith("+"):
            out.append(f"        {stripped}")
    if current_class:
        out.append("    }")
    for rel in sections.get("RELATIONS", "").split("\n"):
        rel = rel.strip()
        if rel:
            out.append(f"    {rel}")
    out.append("```")
    return "\n".join(out)


def render_state_mermaid(sections):
    out = ["```mermaid", "stateDiagram-v2"]
    if sections.get("TITLE"):
        out.append(f"    %% {sections['TITLE']}")
    for s in sections.get("STATES", "").split("\n"):
        s = s.strip().lstrip("-").strip()
        if s:
            out.append(f"    {s}")
    for t in sections.get("TRANSITIONS", "").split("\n"):
        t = t.strip()
        if t:
            out.append(f"    {t}")
    out.append("```")
    return "\n".join(out)


def render_gantt_mermaid(sections):
    out = ["```mermaid", "gantt"]
    if sections.get("TITLE"):
        out.append(f"    title {sections['TITLE']}")
    out.append("    dateFormat YYYY-MM-DD")
    current_section = None
    for line in sections.get("SECTIONS", "").split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") and ":" in stripped:
            header, rest = stripped.lstrip("-").strip().split(":", 1)
            if not rest.strip():
                current_section = header
                out.append(f"\n    section {current_section}")
        elif stripped.startswith("-"):
            entry = stripped.lstrip("-").strip()
            parts = entry.split(",")
            if len(parts) >= 2:
                name_and_time = parts[0].split(":", 1)
                if len(name_and_time) == 2:
                    task = name_and_time[0].strip()
                    start = name_and_time[1].strip()
                    duration = parts[1].strip()
                    task_id = re.sub(r"\W+", "_", task.lower())
                    out.append(f"    {task} :{task_id}, {start}, {duration}")
    out.append("```")
    return "\n".join(out)


RENDERERS = {
    ("flowchart", "mermaid"): render_flowchart_mermaid,
    ("flowchart", "plantuml"): render_flowchart_plantuml,
    ("sequence", "mermaid"): render_sequence_mermaid,
    ("class", "mermaid"): render_class_mermaid,
    ("state", "mermaid"): render_state_mermaid,
    ("gantt", "mermaid"): render_gantt_mermaid,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?")
    ap.add_argument("--engine", choices=["mermaid", "plantuml"], default="mermaid")
    ap.add_argument("--type", choices=list(TEMPLATES.keys()))
    ap.add_argument("--template", choices=list(TEMPLATES.keys()))
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    if args.template:
        print(TEMPLATES[args.template])
        return 0

    if not args.input:
        text = sys.stdin.read()
    else:
        text = pathlib.Path(args.input).read_text(encoding="utf-8")

    sections = parse_structured(text)
    diag_type = args.type or sections.get("TYPE", "flowchart").lower()

    key = (diag_type, args.engine)
    if key not in RENDERERS:
        print(f"[ERR] combinazione non supportata: {diag_type} + {args.engine}", file=sys.stderr)
        print(f"Supportati: {list(RENDERERS.keys())}", file=sys.stderr)
        return 2

    out = RENDERERS[key](sections)
    if args.output:
        pathlib.Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"[OK] {args.output}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
