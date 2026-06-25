#!/usr/bin/env bash
# Poll the Forgejo Actions run for a given commit until it finishes (or times out).
# Usage: FORGEJO_TOKEN=xxx ./scripts/wait_forgejo_ci.sh [commit_sha]
# Writes progress to scripts/ci_wait.log and a final one-line status to scripts/ci_status.txt
set -u

BASE="https://forgejo.home.liteapp.fr/api/v1"
REPO="alexis/magev_planner"
TOK="${FORGEJO_TOKEN:-}"
SHA="${1:-$(git rev-parse HEAD)}"
TIMEOUT="${TIMEOUT:-1800}"   # seconds
INTERVAL="${INTERVAL:-15}"

LOG="$(dirname "$0")/ci_wait.log"
STATUS="$(dirname "$0")/ci_status.txt"
: > "$LOG"

api() { curl -s -H "Authorization: token $TOK" "$BASE/$1"; }

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

log "Waiting for CI on $REPO @ ${SHA:0:8} (timeout ${TIMEOUT}s)"

start=$(date +%s)
while :; do
  now=$(date +%s)
  if (( now - start > TIMEOUT )); then
    log "TIMEOUT after ${TIMEOUT}s"
    echo "timeout" > "$STATUS"
    exit 1
  fi

  runs_json="$(api "repos/$REPO/actions/tasks")"
  # Find the run matching our SHA (fall back to most recent if none match yet).
  read -r run_status conclusion run_id < <(python3 - "$SHA" <<'PY'
import sys, json
sha = sys.argv[1]
try:
    data = json.load(sys.stdin)
except Exception:
    print("none none none"); sys.exit()
runs = data.get("workflow_runs", [])
match = None
for r in runs:
    if r.get("head_sha") == sha:
        match = r; break
if match is None and runs:
    match = runs[0]
if match is None:
    print("none none none")
else:
    print(match.get("status", "?"), match.get("conclusion") or "-", match.get("id", "?"))
PY
  ) <<<"$runs_json"

  if [[ "$run_status" == "none" ]]; then
    log "no run registered yet..."
  else
    log "run #$run_id status=$run_status conclusion=$conclusion"
    case "$run_status" in
      success|completed|failure|cancelled|error|skipped)
        echo "$run_status:$conclusion:#$run_id" > "$STATUS"
        log "DONE -> $run_status / $conclusion"
        exit 0
        ;;
    esac
    # Some Forgejo versions report only conclusion when finished.
    case "$conclusion" in
      success|failure|cancelled|error|skipped)
        echo "$run_status:$conclusion:#$run_id" > "$STATUS"
        log "DONE -> $run_status / $conclusion"
        exit 0
        ;;
    esac
  fi
  sleep "$INTERVAL"
done
