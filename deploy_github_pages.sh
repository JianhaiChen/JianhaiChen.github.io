#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${1:-JianhaiChen}"
REPO="${USER_NAME}.github.io"
REMOTE_URL="${2:-git@github.com:${USER_NAME}/${REPO}.git}"

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"
git push -u origin main

echo "Published target: https://${USER_NAME}.github.io/"
