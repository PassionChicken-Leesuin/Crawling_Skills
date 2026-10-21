#!/usr/bin/env bash
# Copy every skill folder in this repo into ~/.claude/skills/ (Claude Code user-level skills).
set -e
DEST="${1:-$HOME/.claude/skills}"
mkdir -p "$DEST"
for d in "$(dirname "$0")"/*/; do
  n=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  rm -rf "$DEST/$n"; cp -R "$d" "$DEST/$n"; echo "installed $n -> $DEST/$n"
done
