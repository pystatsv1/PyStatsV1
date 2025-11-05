#!/usr/bin/env bash
set -euo pipefail
git checkout dev
git fetch origin
git reset --hard origin/main
git push -f origin dev
