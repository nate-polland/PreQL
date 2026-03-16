#!/bin/bash
# bq_async.sh — Submit a BigQuery query async, monitor for 60s, retrieve via temp table.
#
# No scratch dataset needed — BQ holds results in an anonymous temp table for 24h.
#
# Usage:
#   Submit:  ./bq_async.sh "<SQL>"
#   Check:   ./bq_async.sh --check [job_id]   (omit job_id to use last submitted)
#   Cancel:  ./bq_async.sh --cancel [job_id]  (omit job_id to use last submitted)

set -uo pipefail

PROJECT="prod-ck-abl-data-53"
JOB_FILE="/tmp/bq_last_job.txt"
MAX_ROWS=1000000

# ── Check mode ────────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--check" ]]; then
  JOB_ID="${2:-$(cat "$JOB_FILE" 2>/dev/null | head -1)}"
  if [[ -z "$JOB_ID" ]]; then
    echo "ERROR: No job ID provided and $JOB_FILE is empty."
    exit 1
  fi

  echo "Checking job: $JOB_ID"
  STATE=$(bq show --project_id="$PROJECT" -j "$JOB_ID" 2>/dev/null \
    | grep -oE 'SUCCESS|DONE|RUNNING|PENDING|FAILURE' | head -1)
  echo "Status: ${STATE:-UNKNOWN}"

  if [[ "$STATE" == "DONE" || "$STATE" == "SUCCESS" ]]; then
    echo "Retrieving results (up to $MAX_ROWS rows)..."
    bq head --max_rows="$MAX_ROWS" --project_id="$PROJECT" -j "$JOB_ID" 2>&1
  elif [[ "$STATE" == "FAILURE" ]]; then
    echo "Job FAILED. Run: bq show --project_id=$PROJECT -j $JOB_ID"
  fi
  exit 0
fi

# ── Cancel mode ───────────────────────────────────────────────────────────────
if [[ "${1:-}" == "--cancel" ]]; then
  JOB_ID="${2:-$(cat "$JOB_FILE" 2>/dev/null | head -1)}"
  if [[ -z "$JOB_ID" ]]; then
    echo "ERROR: No job ID provided and $JOB_FILE is empty."
    exit 1
  fi
  echo "Cancelling job: $JOB_ID"
  bq cancel --project_id="$PROJECT" "$JOB_ID" 2>&1
  exit 0
fi

# ── Submit mode ───────────────────────────────────────────────────────────────
SQL="${1:?Usage: ./bq_async.sh \"<SQL>\"}"

echo "Submitting async BigQuery job..."
JOB_OUTPUT=$(bq query \
  --project_id="$PROJECT" \
  --use_legacy_sql=false \
  --nosync \
  "$SQL" 2>&1)

JOB_ID=$(echo "$JOB_OUTPUT" | grep -oE 'bqjob_[a-zA-Z0-9_]+' | head -1)

if [[ -z "$JOB_ID" ]]; then
  echo "ERROR: Could not extract job ID. Output:"
  echo "$JOB_OUTPUT"
  exit 1
fi

echo "$JOB_ID" > "$JOB_FILE"
echo "Job submitted: $JOB_ID"
echo "Monitoring for 60 seconds..."

# ── Monitor loop ──────────────────────────────────────────────────────────────
ELAPSED=0
INTERVAL=5
while [[ $ELAPSED -lt 60 ]]; do
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))

  STATE=$(bq show --project_id="$PROJECT" -j "$JOB_ID" 2>/dev/null \
    | grep -oE 'SUCCESS|DONE|RUNNING|PENDING|FAILURE' | head -1)

  if [[ "$STATE" == "DONE" || "$STATE" == "SUCCESS" ]]; then
    echo "✓ Completed in ~${ELAPSED}s — retrieving results..."
    bq head --max_rows="$MAX_ROWS" --project_id="$PROJECT" -j "$JOB_ID" 2>&1
    exit 0
  elif [[ "$STATE" == "FAILURE" ]]; then
    echo "✗ Job FAILED after ~${ELAPSED}s. Run: bq show --project_id=$PROJECT -j $JOB_ID"
    exit 1
  fi

  echo "  [${ELAPSED}s] ${STATE:-UNKNOWN}..."
done

# ── Timeout handoff ───────────────────────────────────────────────────────────
echo ""
echo "Query still running after 60s. Results will be available for 24h."
echo "Job ID: $JOB_ID (saved to $JOB_FILE)"
echo "Ask me to check in when ready, or run: ./bq_async.sh --check"
