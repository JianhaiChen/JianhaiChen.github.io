#!/usr/bin/env bash
set -euo pipefail

message="${1:-Update site}"

python3 build_blogs.py
git add .
git commit -m "$message" || {
  echo "No changes to commit."
  exit 0
}
git push
