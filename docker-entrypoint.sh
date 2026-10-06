#!/usr/bin/env bash
set -Eeuo pipefail

API_PID=""
WEB_PID=""

stop_children() {
  trap - INT TERM
  for pid in "${API_PID:-}" "${WEB_PID:-}"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" 2>/dev/null || true
    fi
  done
  if [[ -n "${API_PID:-}" ]]; then wait "$API_PID" 2>/dev/null || true; fi
  if [[ -n "${WEB_PID:-}" ]]; then wait "$WEB_PID" 2>/dev/null || true; fi
}

on_signal() {
  local status="$1"
  stop_children
  exit "$status"
}

trap 'on_signal 143' TERM
trap 'on_signal 130' INT

if [[ -z "${DATABASE_URL:-}" ]]; then
  printf '%s\n' 'WARNING: DATABASE_URL is not set; API data routes require an externally reachable PostgreSQL database.' >&2
fi

cd /app
python -m uvicorn app.main:app --app-dir /app/backend --host 127.0.0.1 --port 8000 &
API_PID=$!

cd /app/apps/web
node node_modules/next/dist/bin/next start -H 0.0.0.0 &
WEB_PID=$!

if wait -n "$API_PID" "$WEB_PID"; then
  exit_code=0
else
  exit_code=$?
fi

stop_children
exit "$exit_code"
