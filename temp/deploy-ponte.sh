#!/bin/bash
# deploy-ponte.sh — Aggiorna i prompt del Castello con il ponte Cowork
# Eseguire una sola volta: bash deploy-ponte.sh

set -euo pipefail

PROMPTS_DIR="$HOME/castello-spawner/prompts"
MCP_CONFIG="$HOME/castello-spawner/mcp-config.json"
REPO="tlonitalia/tlon"

echo "=== Deploy Ponte Cowork ==="
echo ""

# 1. Scarica i prompt aggiornati da tlon/temp/
echo "Scarico i prompt aggiornati..."
for file in contesto.md vedetta.md paladino.md custode.md; do
    echo "  $file"
    gh api "repos/$REPO/contents/temp/$file" -q '.content' | base64 -d > "$PROMPTS_DIR/$file"
done
echo "  Fatto."

# 2. Verifica che tlon_push_file sia disponibile nella config MCP
echo ""
echo "Verifico config MCP per tlon_push_file..."
if command -v jq &> /dev/null; then
    if jq -e '.mcpServers.tlon' "$MCP_CONFIG" > /dev/null 2>&1; then
        echo "  Server tlon trovato nella config MCP."
        echo "  Verifica manualmente che il server tlon supporti push_file."
        echo "  (Se è lo stesso tipo dei tool Cowork, push_file è già disponibile.)"
    else
        echo "  ATTENZIONE: server 'tlon' non trovato in $MCP_CONFIG"
        echo "  I vassalli non potranno depositare nel mirror."
    fi
else
    echo "  jq non installato, salto verifica. Controlla manualmente."
fi

# 3. Mostra diagnostica Paladino
echo ""
echo "=== Diagnostica Paladino ==="
LOG_DIR="$HOME/castello-spawner/logs"
TODAY=$(date +%Y-%m-%d)

echo "Log del Paladino (non lavoro!):"
if [[ -f "$LOG_DIR/${TODAY}-paladino.log" ]]; then
    echo "  File trovato: $LOG_DIR/${TODAY}-paladino.log"
    echo "  Ultime 20 righe:"
    tail -20 "$LOG_DIR/${TODAY}-paladino.log"
else
    echo "  NESSUN LOG TROVATO: $LOG_DIR/${TODAY}-paladino.log"
    echo "  Il Paladino potrebbe non essere stato lanciato oggi."
    echo ""
    echo "  Controlla lo spawner.log:"
    grep -i "paladin" "$LOG_DIR/spawner.log" 2>/dev/null || echo "  Nessuna menzione del Paladino nello spawner.log"
fi

echo ""
echo "=== Deploy completato ==="
echo "I vassalli ora depositeranno copie in tlon/temp/castello/"
echo "Il Cowork potrà leggere l'output del Castello via tlon_read_file."
