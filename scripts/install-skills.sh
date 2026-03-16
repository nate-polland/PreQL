#!/bin/bash
# install-skills.sh
# Creates symlinks from ~/.claude/skills/ → PreQL/skills/
# Run once after cloning. Re-running is safe (idempotent).
# Because these are symlinks, pulling updates to the repo automatically
# updates the skills — no need to re-run this script.

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
SKILLS_DST="$HOME/.claude/skills"

mkdir -p "$SKILLS_DST"

echo "Installing PreQL skills from $SKILLS_SRC → $SKILLS_DST"
echo ""

for skill_dir in "$SKILLS_SRC"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$SKILLS_DST/$skill_name"

  if [ -L "$target" ]; then
    echo "  ✓ $skill_name (already linked)"
  elif [ -d "$target" ]; then
    echo "  ⚠ $skill_name — directory already exists at $target (not a symlink, skipping)"
    echo "    To replace it: rm -rf \"$target\" && re-run this script"
  else
    ln -s "$skill_dir" "$target"
    echo "  ✓ $skill_name (linked)"
  fi
done

echo ""
echo "Done. Restart Claude Code for skills to take effect."
