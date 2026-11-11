#!/usr/bin/env bash
# Install the skills into a Claude Code skills folder (default ~/.claude/skills).
#   ./install.sh                 copy
#   ./install.sh --link          symlink, so a git pull updates them
#   ./install.sh --dir PATH      another skills folder (e.g. a project's .claude/skills)
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DEST="$HOME/.claude/skills"; LINK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --link) LINK=1 ;;
    --dir) DEST="$2"; shift ;;
    -h|--help) sed -n 2,5p "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac; shift
done
mkdir -p "$DEST"
for s in orchestra council chatgpt-lane kimi-lane deepseek-lane; do
  if [ -e "$DEST/$s" ] && [ ! -L "$DEST/$s" ]; then
    echo "skip $s: $DEST/$s already exists (remove it first to replace)"; continue
  fi
  rm -f "$DEST/$s"
  if [ $LINK -eq 1 ]; then ln -s "$SRC/$s" "$DEST/$s"; else cp -R "$SRC/$s" "$DEST/$s"; fi
  echo "installed $s -> $DEST/$s"
done
# The lane skills call the runner as ../orchestra/scripts/..., so all skills must sit side by side.
chmod +x "$DEST/orchestra/scripts/"mmo-* 2>/dev/null || true
"$DEST/orchestra/scripts/mmo-preflight" || true
