#!/bin/bash
# .claude/hooks/backup-md.sh
# PreToolUse hook: backs up .md files before Edit or Write operations.
# Keeps only the 2 most recent backups per file; older ones are auto-deleted.

# Read the tool input JSON from Claude Code via stdin
INPUT=$(cat)

# Extract the target file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only act on .md files
if [[ -n "$FILE_PATH" && "$FILE_PATH" == *.md ]]; then
    BACKUP_DIR=".claude/backups"
    mkdir -p "$BACKUP_DIR"

    BASENAME=$(basename "$FILE_PATH")
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/${BASENAME}_${TIMESTAMP}.md"

    # Back up only if the file currently exists
    if [[ -f "$FILE_PATH" ]]; then
        cp "$FILE_PATH" "$BACKUP_FILE"

        # Keep only the 2 most recent backups for this file; delete older ones
        ls -t "$BACKUP_DIR/${BASENAME}"_*.md 2>/dev/null | tail -n +3 | xargs -I {} rm "{}"
    fi
fi

# Exit 0 allows Claude to proceed with the edit
exit 0
