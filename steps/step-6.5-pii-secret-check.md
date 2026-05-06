# Step 6.5 — PII & Secret check (prima del write finale)

Opzionale. Attivato di default per tipologie `analisi-codice`, `bug`, `codice` (output che potrebbe contenere dati sensibili). Sempre attivo se utente passa `--public` (relazione destinata a pubblicazione esterna).

## PII redaction

Lo script `scripts/security/pii-redact.py <file> [--mode=warn|redact]` scansiona per:

- **Email**: regex `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **IP address** (v4 + v6)
- **Hostname** interni: `*.internal`, `*.local`, `*.lan`, `localhost`
- **Path locali Windows**: `C:\\Users\\*`, `D:\\*` ecc.
- **Path locali Unix**: `/home/*`, `/Users/*`
- **Numeri di telefono** (formato IT: `+39`, `3xx xxxxxxx`)
- **Codici fiscali** (regex IT)
- **P.IVA** (regex IT 11 cifre)
- **IBAN** (regex generico)
- **Carte di credito** (regex Luhn-validate)

Modalità:
- `warn` (default in interactive): elenca occorrenze + numero riga, chiede conferma per ognuna
- `redact`: sostituisce con placeholder (`[EMAIL_REDACTED]`, `[IP_REDACTED]`, `[USER_PATH]`, ecc.)

## Secret scan (per code snippet inclusi)

Lo script `scripts/security/secret-scan.sh <file>` cerca pattern noti:

- AWS access key: `AKIA[0-9A-Z]{16}`
- AWS secret: regex base64 40-char
- GitHub token: `ghp_*`, `gho_*`, `ghs_*`, `ghr_*`
- Anthropic API key: `sk-ant-*`
- OpenAI: `sk-[A-Za-z0-9]{48}`
- Google API key: `AIza[0-9A-Za-z\\-_]{35}`
- Slack token: `xox[bpoa]-*`
- Stripe: `sk_live_*`, `pk_live_*`
- Generic: `password\s*=\s*['"]\w+['"]`, `apikey\s*=`, `secret\s*=`
- Private keys: `-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----`
- JWT tokens: `eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+`
- `.env` file content patterns
- Database URLs con credenziali

**Modalità sempre `warn` + bloccante**: se trovato anche un solo secret, BLOCCA il write finale e chiedi conferma esplicita all'utente. La risposta default è "rimuovi/sostituisci".

## Comportamento

```
=== PII / SECRET SCAN ===

[PII] Email trovate (3):
  - line 234: mario.rossi@azienda.com
  - line 456: info@cliente.it
  - line 789: support@fornitore.com

[PII] Path locali (5):
  - line 12: C:\Users\domin\Documents\progetto
  - line 87: /Users/marco/dev
  - ...

[SECRET] AWS key in code block:
  - line 567: AKIAIOSFODNN7EXAMPLE
  ⚠️  BLOCCANTE — rimuovi prima di consegnare.
```

`AskUserQuestion` con opzioni:
- `Sostituisci tutto con placeholder` (modalità `--redact`)
- `Lascio tutto, è interno` (sblocca)
- `Mostrami uno per uno` (interactive review)

## Eccezioni accettabili

- Email del committente nel frontespizio (è il destinatario, non leak)
- Path nei comandi di esempio della relazione (es. `cd /var/www`)
- Hostname pubblici di servizi (es. `api.stripe.com`)

L'utente dichiara queste eccezioni in modalità interactive review.

## Modalità `--public`

Sempre attiva per relazioni destinate a:
- Pubblicazione su GitHub
- Articolo blog
- Allegato a candidatura/CV
- Submission a conferenza/rivista

Default conservativo: tutti i path locali → placeholder, tutti gli IP → `[IP]`, tutti gli hostname interni → `[INTERNAL_HOST]`.
