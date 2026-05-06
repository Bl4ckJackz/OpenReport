#!/usr/bin/env python3
"""resolve-variables.py — Sostituisce placeholder {{var_name}} nel testo.

Legge le variabili da:
1. session-state.json (variables + cover)
2. brand-profile attivo (se brand_profile settato)
3. user-profile (per autore/email/ente)
4. CLI --set key=value (override)

Usage:
    python3 resolve-variables.py <file_md_or_tex> --state <path> [--brand <name>] [--set k=v]...
    python3 resolve-variables.py --scan <file>           # elenca placeholder non risolti
    python3 resolve-variables.py --list-available --state <path>

Placeholder supportati (non esaustivo):
    {{client_name}}         da state.cover.cliente
    {{project_code}}        da state.cover.progetto_codice
    {{contract_id}}         da state.cover.contratto_id
    {{doc_id}}              da state.cover.doc_id
    {{doc_version}}         da state.cover.versione
    {{doc_status}}          da state.cover.status
    {{classification}}      da state.cover.classificazione (uppercase)
    {{delivery_date}}       da state.answers.scadenza
    {{author}}              da state.cover.autore
    {{author_email}}        da user-profile.email
    {{company_name}}        da brand.ragione_sociale
    {{company_claim}}       da brand.claim
    {{company_vat}}         da brand.p_iva
    {{company_website}}     da brand.sito_web
    {{today}}               data corrente YYYY-MM-DD
    {{year}}                anno corrente
"""

import argparse
import json
import pathlib
import re
import sys
from datetime import date, datetime

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


def load_json(path):
    p = pathlib.Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERR] JSON invalido {path}: {e}", file=sys.stderr)
        return {}


def get_brand(brand_profile, active_name=None):
    brands = brand_profile.get("brands", []) if isinstance(brand_profile, dict) else []
    if not brands:
        return {}
    if active_name:
        for b in brands:
            if b.get("nome") == active_name:
                return b
    default_name = brand_profile.get("active_brand")
    if default_name:
        for b in brands:
            if b.get("nome") == default_name:
                return b
    return brands[0]


def build_variables(state, user_profile, brand):
    cover = state.get("cover", {}) or {}
    answers = state.get("answers", {}) or {}
    custom = state.get("variables", {}) or {}

    today = date.today().isoformat()
    year = str(date.today().year)

    vars_map = {
        # Cover
        "client_name": cover.get("cliente", ""),
        "project_code": cover.get("progetto_codice", ""),
        "contract_id": cover.get("contratto_id", ""),
        "doc_id": cover.get("doc_id", ""),
        "doc_version": cover.get("versione", ""),
        "doc_status": (cover.get("status") or "").upper(),
        "classification": (cover.get("classificazione") or "").upper(),
        "protocollo": cover.get("protocollo", ""),
        "delivery_date": answers.get("scadenza", "") or "",
        "author": cover.get("autore", "") or user_profile.get("nome_completo", ""),
        "author_email": user_profile.get("email", ""),
        "author_role": user_profile.get("ruolo_default", ""),
        "ente": cover.get("ente", "") or user_profile.get("ente_default", ""),
        "title": cover.get("titolo", ""),
        "subtitle": cover.get("sottotitolo", ""),
        # Brand
        "company_name": brand.get("ragione_sociale", ""),
        "company_claim": brand.get("claim", ""),
        "company_vat": brand.get("p_iva", ""),
        "company_address": brand.get("indirizzo", ""),
        "company_website": brand.get("sito_web", ""),
        "company_email": brand.get("email_default", ""),
        "company_phone": brand.get("telefono", ""),
        "company_sdi": brand.get("sdi", ""),
        "company_pec": brand.get("pec", ""),
        # Time
        "today": today,
        "year": year,
        "now": datetime.now().isoformat(timespec="minutes"),
    }
    # Custom overrides
    vars_map.update({k: str(v) for k, v in custom.items()})
    return vars_map


def resolve(text, vars_map):
    def sub(match):
        key = match.group(1)
        if key in vars_map:
            return str(vars_map[key])
        return match.group(0)
    return PLACEHOLDER_RE.sub(sub, text)


def find_unresolved(text):
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--state", help="Path session-state.json")
    ap.add_argument("--brand-profile", default=None, help="Path .brand-profile.json")
    ap.add_argument("--user-profile", default=None, help="Path .user-profile.json")
    ap.add_argument("--brand", help="Nome brand da usare (override active_brand)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="Override variabile inline")
    ap.add_argument("--scan", action="store_true", help="Lista placeholder non risolti, senza sostituire")
    ap.add_argument("--list-available", action="store_true", help="Lista variabili disponibili")
    ap.add_argument("--in-place", action="store_true", help="Scrive sul file (altrimenti stdout)")
    args = ap.parse_args()

    skill_dir = pathlib.Path(__file__).resolve().parent.parent
    brand_path = args.brand_profile or (skill_dir / ".brand-profile.json")
    user_path = args.user_profile or (skill_dir / ".user-profile.json")

    state = load_json(args.state) if args.state else {}
    user_profile = load_json(user_path)
    brand_profile = load_json(brand_path)

    brand_active = args.brand or state.get("answers", {}).get("brand_profile")
    brand = get_brand(brand_profile, brand_active)

    vars_map = build_variables(state, user_profile, brand)
    for override in args.set:
        if "=" in override:
            k, v = override.split("=", 1)
            vars_map[k.strip()] = v

    if args.list_available:
        for k in sorted(vars_map.keys()):
            val = vars_map[k]
            preview = (val[:50] + "...") if len(val) > 53 else val
            print(f"  {{{{{k}}}}} = {preview!r}")
        return 0

    if not args.file:
        print("Usage: resolve-variables.py <file> --state <path> [opts]", file=sys.stderr)
        return 2

    text = pathlib.Path(args.file).read_text(encoding="utf-8")

    if args.scan:
        unresolved = find_unresolved(text)
        if not unresolved:
            print("[OK] Nessun placeholder non risolto")
            return 0
        print(f"[WARN] {len(unresolved)} placeholder non risolti:")
        for k in unresolved:
            print(f"  {{{{{k}}}}}")
        return 1

    resolved_text = resolve(text, vars_map)
    remaining = find_unresolved(resolved_text)

    if args.in_place:
        pathlib.Path(args.file).write_text(resolved_text, encoding="utf-8")
        substituted = sum(1 for _ in PLACEHOLDER_RE.finditer(text)) - len(remaining)
        print(f"[OK] {substituted} placeholder sostituiti in {args.file}")
        if remaining:
            print(f"[WARN] {len(remaining)} non risolti: {', '.join('{{'+k+'}}' for k in remaining)}")
    else:
        print(resolved_text)
        if remaining:
            print(f"\n[WARN] {len(remaining)} placeholder non risolti: {', '.join(remaining)}", file=sys.stderr)

    return 0 if not remaining else 1


if __name__ == "__main__":
    sys.exit(main())
