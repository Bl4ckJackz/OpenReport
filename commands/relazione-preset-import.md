---
description: Importa preset /relazione da URL (gist/GitHub), condividi preset con team
argument-hint: "<url|path|gist-id>"
---

# /relazione-preset-import — Template marketplace

Importa preset YAML di `/relazione` da fonti esterne: URL pubblico, GitHub gist, path locale.

## Casi d'uso

- **Team sync**: condividi preset "status-report-weekly-azienda" fra colleghi
- **Community**: scarica preset per casi d'uso comuni (es. tesi di un ateneo specifico)
- **Versioning**: mantieni preset in git repo team, tutti usano stessa versione

## Cosa fare quando invocato

### Input: URL

```
/relazione-preset-import https://raw.githubusercontent.com/team/presets/main/weekly-status.yaml
```

1. `curl -fsSL <url>` → scarica contenuto
2. Verifica che sia valid YAML con campi `profile_name`, `answers`
3. `AskUserQuestion`: "Importare come `<nome-proposto>`?"
4. Salva in `~/.claude/skills/relazione/presets/<nome>.yaml`
5. Chiedi conferma: "Test preset ora?" → se sì, mostra con `/relazione-quick --profile=<nome>`

### Input: GitHub gist

```
/relazione-preset-import gist:abc123def456
```

1. `curl -fsSL https://gist.githubusercontent.com/raw/abc123def456` → scarica
2. Come sopra

### Input: path locale

```
/relazione-preset-import ~/Downloads/preset.yaml
```

Copia diretta dopo validazione.

## Validazione

Prima di salvare, verifica:
- [ ] YAML valido
- [ ] `profile_name` presente (string)
- [ ] `answers.tipologia` in enum supportato
- [ ] `answers.lingua` valida
- [ ] Non contiene path assoluti a file esterni (security)
- [ ] Non contiene credenziali (email/API key — match regex)
- [ ] Nome file sicuro (no `../`, no spazi)

## Export

Comando inverso: `/relazione-preset-export <nome>`:
1. Trova `presets/<nome>.yaml`
2. `AskUserQuestion`: "Pubblica come gist pubblico / privato / copia stdout?"
3. Se gist: usa `gh gist create` se disponibile
4. Altrimenti stampa contenuto

## Red flags

- **Mai eseguire arbitrary code** da preset (YAML safe-load, mai `yaml.load`)
- **Mai** importare preset che includono `post_actions` con comandi shell (solo lista statica di nomi)
- **Warn** se preset ha `cover_defaults` con nomi propri (potrebbero essere copy-paste dimenticate)
- **Timeout** curl 10s max, dimensione max 100KB (preset non devono contenere dati)

## Registry pubblico

Mantieni un manifest condiviso (repo team o gist comune) con:
```yaml
# preset-registry.yaml
presets:
  - name: acme-status-weekly
    url: https://example.com/presets/acme-status.yaml
    description: Status weekly per cliente ACME
    author: team-sales
  - name: thesis-unipd
    url: https://example.com/presets/unipd-tesi.yaml
    description: Template tesi Università di Padova
```

Comando `/relazione-preset-registry` (futuro) elenca e filtra.
