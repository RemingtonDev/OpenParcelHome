#!/bin/bash
set -eu
umask 077
cd "$(dirname "$0")/.."
mkdir -p .local/reports
report="$(mktemp .local/reports/preflight.XXXXXX)"
{
  date -u '+Recorded UTC: %Y-%m-%dT%H:%M:%SZ'
  sw_vers
  uname -m
  sysctl -n hw.memsize
  for tool in git gh python3 brew jadx apktool; do
    command -v "$tool" || true
  done
  python3 --version
  xcode-select -p
} > "$report"
echo "Saved local environment report: $report"
