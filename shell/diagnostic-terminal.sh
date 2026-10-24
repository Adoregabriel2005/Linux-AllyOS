#!/bin/sh
# Manter relatórios curtos visíveis; argumentos são passados sem eval.
"$@"
rose_diagnostic_result=$?
printf '\n[Enter / Return]\n'
read -r rose_diagnostic_reply
exit "$rose_diagnostic_result"
