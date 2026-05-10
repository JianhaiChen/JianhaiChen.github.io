#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${1:-JianhaiChen}"
REPO="${USER_NAME}.github.io"
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"

if [[ -z "$TOKEN" ]]; then
  printf "GitHub token: "
  stty -echo
  read -r TOKEN
  stty echo
  printf "\n"
fi

status="$(curl -s -o /tmp/github-repo-check.json -w "%{http_code}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${USER_NAME}/${REPO}")"

if [[ "$status" == "404" ]]; then
  curl -fsS \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"${REPO}\",\"private\":false,\"auto_init\":false}" >/dev/null
elif [[ "$status" != "200" ]]; then
  echo "GitHub repo check failed with HTTP ${status}."
  cat /tmp/github-repo-check.json
  exit 1
fi

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${USER_NAME}/${REPO}.git"
git push "https://x-access-token:${TOKEN}@github.com/${USER_NAME}/${REPO}.git" main:main

curl -s \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${USER_NAME}/${REPO}/pages" >/tmp/github-pages-check.json

if ! grep -q '"html_url"' /tmp/github-pages-check.json; then
  curl -s \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -X POST \
    "https://api.github.com/repos/${USER_NAME}/${REPO}/pages" \
    -d '{"source":{"branch":"main","path":"/"}}' >/tmp/github-pages-create.json || true
fi

echo "Published target: https://${USER_NAME}.github.io/"
