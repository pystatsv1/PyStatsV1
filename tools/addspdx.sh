#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob
for f in scripts/*.py; do
  if ! grep -q "SPDX-License-Identifier: MIT" "$f"; then
    # prepend the line (portable)
    tmp="$(mktemp)"
    printf '# SPDX-License-Identifier: MIT\n' > "$tmp"
    cat "$f" >> "$tmp"
    mv "$tmp" "$f"
  fi
done
