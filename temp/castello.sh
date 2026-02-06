#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# IL CASTELLO — Spawner v3
# Agente persistente per Andrea Colamedici e Maura Gancitano
# Gira sul Mac, usa Claude Code con account Max (Opus 4.6)
#
# Uso:
#   ./castello.sh briefing     — Briefing mattutino (rapido, ~5 min)
#   ./castello.sh lavoro       — Lavoro profondo (produzione, ~15 min)
#   ./castello.sh revisione    — Revisione qualità (controllo, ~10 min)
#   ./castello.sh newsletter   — Produzione Tlonletter (~15 min)
#   ./castello.sh              — Default: briefing
#
# Il ciclo completo consigliato è:
#   07:00  briefing     → analizza stato, identifica priorità
#   08:00  lavoro       → produce materiali per il progetto più urgente
#   12:00  lavoro       → seconda sessione di produzione
#   18:00  revisione    → controlla qualità di ciò che è stato prodotto
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Cleanup ───────────────────────────────────────────────────────
# Quando lo script termina (per qualsiasi ragione), uccide tutti
# i processi figli — in particolare i processi mcp-remote che
# mantengono le connessioni SSE aperte e impediscono l'uscita.
cleanup() {
    local children
    children=$(jobs -p 2>/dev/null)
    if [[ -n "$children" ]]; then
        kill $children 2>/dev/null
        wait $children 2>/dev/null
    fi
    # Uccide anche eventuali mcp-remote orfani lanciati da questa sessione
    pkill -P $$ 2>/dev/null || true
}
trap cleanup EXIT

# ── Configurazione ──────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MCP_CONFIG="$SCRIPT_DIR/castello-mcp.json"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
LOG_DIR="$SCRIPT_DIR/logs"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%H:%M)
MODALITA="${1:-briefing}"

# ── Generatore di nomi ────────────────────────────────────────────
# Ogni sessione del Castello è un cavaliere che nasce, lavora,
# e firma il proprio lavoro. Il nome viene scelto combinando
# un attributo e un riferimento, poi registrato nel log.

ATTRIBUTI=(
  Vigile Tenace Paziente Lucido Fedele Silente
  Costante Attento Sottile Austero Fermo Sobrio
  Acuto Mite Lento Preciso Onesto Devoto
  Quieto Grave Pronto Limpido Severo Solerte
)

RIFERIMENTI=(
  "della Soglia" "del Margine" "della Torre" "del Ponte"
  "della Biblioteca" "del Chiostro" "della Memoria" "del Labirinto"
  "della Lanterna" "del Giardino" "della Mappa" "del Silenzio"
  "della Veglia" "del Pozzo" "della Bussola" "del Varco"
  "della Pagina" "del Fuoco" "della Scala" "del Confine"
  "della Cripta" "del Cortile" "della Volta" "del Passaggio"
)

# Selezione pseudo-casuale basata su data+ora (riproducibile per la stessa sessione)
SEED=$(date +%s)
ATTR_IDX=$(( SEED % ${#ATTRIBUTI[@]} ))
RIF_IDX=$(( (SEED / ${#ATTRIBUTI[@]}) % ${#RIFERIMENTI[@]} ))
CAVALIERE="Ser ${ATTRIBUTI[$ATTR_IDX]} ${RIFERIMENTI[$RIF_IDX]}"

# ── Validazione ─────────────────────────────────────────────────

if [[ ! "$MODALITA" =~ ^(briefing|lavoro|revisione|newsletter)$ ]]; then
    echo "Errore: modalità sconosciuta '$MODALITA'"
    echo "Uso: $0 [briefing|lavoro|revisione|newsletter]"
    exit 1
fi

if [[ ! -f "$MCP_CONFIG" ]]; then
    echo "Errore: castello-mcp.json non trovato in $SCRIPT_DIR"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo "Errore: claude non trovato nel PATH."
    echo "Installa Claude Code: sudo npm install -g @anthropic-ai/claude-code"
    exit 1
fi

# ── Preparazione ────────────────────────────────────────────────

mkdir -p "$LOG_DIR"

# ── Assemblaggio del prompt ─────────────────────────────────────
# Il prompt è composto da cinque parti:
#   1. Contesto fisso (chi sei, chi sono loro, come scrivono, strumenti)
#   2. Memoria di lavoro (ciò che il Castello ha imparato, se esiste)
#   3. Prompt specifico della modalità
#   4. Identità del cavaliere
#   5. Metadati di sessione (data, ora, modalità)

CONTESTO_FILE="$PROMPTS_DIR/contesto.md"
MEMORIA_FILE="$PROMPTS_DIR/memoria.md"
MODALITA_FILE="$PROMPTS_DIR/${MODALITA}.md"

if [[ ! -f "$CONTESTO_FILE" ]]; then
    echo "Errore: contesto.md non trovato in $PROMPTS_DIR"
    exit 1
fi

if [[ ! -f "$MODALITA_FILE" ]]; then
    echo "Errore: ${MODALITA}.md non trovato in $PROMPTS_DIR"
    exit 1
fi

CONTESTO=$(cat "$CONTESTO_FILE")
MODALITA_PROMPT=$(cat "$MODALITA_FILE")

# La memoria è opzionale: se esiste la include, altrimenti prosegue.
MEMORIA=""
if [[ -f "$MEMORIA_FILE" ]]; then
    MEMORIA=$(cat "$MEMORIA_FILE")
fi

PROMPT="$CONTESTO

---

$MEMORIA

---

$MODALITA_PROMPT

---

Il tuo nome è $CAVALIERE. Sei il cavaliere di questa sessione del Castello. Firma il tuo lavoro con questo nome nel log e nei materiali che depositi. Quando aggiorni log.json nel repository castello, includi il campo \"cavaliere\": \"$CAVALIERE\" nella entry della sessione.

Data di oggi: $TODAY
Ora: $NOW
Modalità: $MODALITA
Sessione ID: ${TODAY}-${NOW}-${MODALITA}"

# ── Timeout per modalità ───────────────────────────────────────
# Ogni modalità ha un tempo massimo. Se Claude non finisce entro
# questo limite, il processo viene terminato. Timeout generoso
# per evitare interruzioni premature, ma evita processi infiniti.

case "$MODALITA" in
    briefing)    TIMEOUT=600  ;;   # 10 minuti
    lavoro)      TIMEOUT=1800 ;;   # 30 minuti
    revisione)   TIMEOUT=900  ;;   # 15 minuti
    newsletter)  TIMEOUT=1800 ;;   # 30 minuti
    *)           TIMEOUT=900  ;;
esac

# ── Esecuzione ──────────────────────────────────────────────────

echo "[$TODAY $NOW] $CAVALIERE — modalità: $MODALITA (timeout: ${TIMEOUT}s)" >> "$LOG_DIR/spawner.log"

# timeout uccide il processo se supera il limite.
# Il trap EXIT si occupa di pulire i figli (mcp-remote).
timeout "$TIMEOUT" claude \
  --print \
  --model opus \
  --mcp-config "$MCP_CONFIG" \
  --dangerously-skip-permissions \
  --max-turns 30 \
  -p "$PROMPT" \
  >> "$LOG_DIR/${TODAY}-${MODALITA}.log" 2>&1

EXIT_CODE=$?

# ── Chiusura ────────────────────────────────────────────────────

FINE=$(date +%H:%M)

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "[$TODAY $FINE] $CAVALIERE ha completato il suo lavoro (exit: 0)" >> "$LOG_DIR/spawner.log"
elif [[ $EXIT_CODE -eq 124 ]]; then
    echo "[$TODAY $FINE] $CAVALIERE è stato richiamato per timeout dopo ${TIMEOUT}s" >> "$LOG_DIR/spawner.log"
else
    echo "[$TODAY $FINE] $CAVALIERE ha incontrato un ostacolo (exit: $EXIT_CODE)" >> "$LOG_DIR/spawner.log"
    echo "[$TODAY $FINE] Controlla $LOG_DIR/${TODAY}-${MODALITA}.log" >> "$LOG_DIR/spawner.log"
fi

exit $EXIT_CODE
