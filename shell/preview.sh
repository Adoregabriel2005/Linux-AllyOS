#!/bin/sh
# Prévia isolada: o encerramento limpa somente os processos criados aqui.
set -eu
cd "$(dirname "$0")"
Xephyr :1 -screen 1000x700 -nolisten tcp &
rose_preview_xpid=$!
rose_preview_session=''
cleanup() {
    [ -z "$rose_preview_session" ] || kill "$rose_preview_session" 2>/dev/null || true
    kill "$rose_preview_xpid" 2>/dev/null || true
    wait "$rose_preview_xpid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM
sleep 2
ROSESHELL_NESTED=1 DISPLAY=:1 .venv/bin/python session.py "$@" &
rose_preview_session=$!
wait "$rose_preview_session"
