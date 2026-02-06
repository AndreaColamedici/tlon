#!/usr/bin/env python3
"""
Aggiorna castello.sh per la gerarchia feudale del Castello.
Introduce la distinzione tra Paladini e Valvassori.
Eseguire una sola volta: python3 aggiorna-castello.py
"""

import os
import sys

SCRIPT = os.path.expanduser('~/castello-spawner/castello.sh')

with open(SCRIPT, 'r') as f:
    content = f.read()

original = content  # backup per verifica

# ─────────────────────────────────────────────────────────
# 1. Aggiorna validazione per accettare i nuovi nomi
# ─────────────────────────────────────────────────────────
content = content.replace(
    'briefing|lavoro|revisione|newsletter',
    'briefing|lavoro|revisione|newsletter|vedetta|paladino|custode',
    1  # solo la prima occorrenza (la regex di validazione)
)

# ─────────────────────────────────────────────────────────
# 2. Inserisci mapping GRADO/CLASSE dopo il blocco di validazione
# ─────────────────────────────────────────────────────────
MARKER = 'if [[ ! -f "$MCP_CONFIG" ]]; then'
MAPPING_BLOCK = '''# ── Gerarchia feudale ───────────────────────────────────────────
# I valvassori tengono il regno (vedetta, custode): sessioni brevi.
# Il Paladino crea (paladino, newsletter): sessioni lunghe e profonde.

case "$MODALITA" in
    briefing|vedetta)   GRADO="Valvassore"; CLASSE="vedetta"   ;;
    lavoro|paladino)    GRADO="Paladino";   CLASSE="paladino"  ;;
    revisione|custode)  GRADO="Valvassore"; CLASSE="custode"   ;;
    newsletter)         GRADO="Paladino";   CLASSE="newsletter" ;;
esac

'''

if MARKER in content and 'GRADO=' not in content:
    content = content.replace(MARKER, MAPPING_BLOCK + MARKER, 1)

# ─────────────────────────────────────────────────────────
# 3. Prompt file: usa CLASSE invece di MODALITA
# ─────────────────────────────────────────────────────────
content = content.replace(
    'MODALITA_FILE="$PROMPTS_DIR/${MODALITA}.md"',
    'MODALITA_FILE="$PROMPTS_DIR/${CLASSE}.md"'
)

# ─────────────────────────────────────────────────────────
# 4. Timeout e MAX_TURNS per classe
# ─────────────────────────────────────────────────────────
OLD_TIMEOUT = '''case "$MODALITA" in
    briefing)    TIMEOUT=600  ;;   # 10 minuti
    lavoro)      TIMEOUT=1800 ;;   # 30 minuti
    revisione)   TIMEOUT=900  ;;   # 15 minuti
    newsletter)  TIMEOUT=1800 ;;   # 30 minuti
    *)           TIMEOUT=900  ;;
esac'''

NEW_TIMEOUT = '''case "$CLASSE" in
    vedetta)     TIMEOUT=900;  MAX_TURNS=15 ;;   # 15 minuti, scansione rapida
    paladino)    TIMEOUT=5400; MAX_TURNS=60 ;;   # 90 minuti, lavoro profondo
    custode)     TIMEOUT=900;  MAX_TURNS=15 ;;   # 15 minuti, revisione serale
    newsletter)  TIMEOUT=1800; MAX_TURNS=30 ;;   # 30 minuti, produzione
    *)           TIMEOUT=900;  MAX_TURNS=15 ;;
esac'''

content = content.replace(OLD_TIMEOUT, NEW_TIMEOUT)

# ─────────────────────────────────────────────────────────
# 5. max-turns variabile
# ─────────────────────────────────────────────────────────
content = content.replace('--max-turns 30', '--max-turns $MAX_TURNS')

# ─────────────────────────────────────────────────────────
# 6. Spawner log con GRADO e CLASSE
# ─────────────────────────────────────────────────────────
content = content.replace(
    'echo "[$TODAY $NOW] $CAVALIERE — modalità: $MODALITA (timeout: ${TIMEOUT}s)" >> "$LOG_DIR/spawner.log"',
    'echo "[$TODAY $NOW] $CAVALIERE ($GRADO) — $CLASSE (timeout: ${TIMEOUT}s, turni: ${MAX_TURNS})" >> "$LOG_DIR/spawner.log"'
)

# ─────────────────────────────────────────────────────────
# 7. Identità cavaliere nel prompt
# ─────────────────────────────────────────────────────────
content = content.replace(
    'Il tuo nome è $CAVALIERE. Sei il cavaliere di questa sessione del Castello.',
    'Il tuo nome è $CAVALIERE. Sei un $GRADO del Castello, in missione come $CLASSE.'
)

# ─────────────────────────────────────────────────────────
# 8. Log di completamento con GRADO
# ─────────────────────────────────────────────────────────
content = content.replace(
    '$CAVALIERE ha completato il suo lavoro',
    '$CAVALIERE ($GRADO) ha completato il suo lavoro'
)
content = content.replace(
    '$CAVALIERE è stato richiamato per timeout',
    '$CAVALIERE ($GRADO) è stato richiamato per timeout'
)
content = content.replace(
    '$CAVALIERE ha incontrato un ostacolo',
    '$CAVALIERE ($GRADO) ha incontrato un ostacolo'
)

# ─────────────────────────────────────────────────────────
# Verifica e scrittura
# ─────────────────────────────────────────────────────────
changes = []
if 'GRADO=' in content:
    changes.append('gerarchia feudale (GRADO/CLASSE)')
if 'MAX_TURNS' in content:
    changes.append('turni variabili per classe')
if '$CLASSE' in content:
    changes.append('prompt per classe')
if 'TIMEOUT=5400' in content:
    changes.append('timeout Paladino 90 min')

if not changes:
    print("Nessuna modifica applicata. Lo script potrebbe essere già aggiornato.")
    sys.exit(1)

# Scrivi backup
with open(SCRIPT + '.bak', 'w') as f:
    f.write(original)

# Scrivi aggiornamento
with open(SCRIPT, 'w') as f:
    f.write(content)

print("castello.sh aggiornato")
print(f"  Backup salvato in {SCRIPT}.bak")
for c in changes:
    print(f"  - {c}")
print()
print("  Valvassori: vedetta (15 min, 15 turni), custode (15 min, 15 turni)")
print("  Paladini:   paladino (90 min, 60 turni), newsletter (30 min, 30 turni)")
