#!/usr/bin/env bash
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$KIT_DIR"

sha256sum -c PYSTATSV1_DROPIN_034_WSL_KIT_SHA256SUMS.txt

if ! grep -Eqi 'wsl2|microsoft-standard' /proc/version 2>/dev/null \
  && ! uname -r | grep -Eqi 'wsl2|microsoft-standard'; then
  echo "ERROR: this proof must run inside Windows 11 WSL2, not native Linux or WSL1" >&2
  exit 2
fi
for command in cmd.exe wsl.exe python3 sha256sum; do
  command -v "$command" >/dev/null || {
    echo "ERROR: required WSL2 proof command not found: $command" >&2
    exit 2
  }
done

case "$KIT_DIR" in
  /mnt/*)
    echo "ERROR: unpack the WSL proof kit inside the WSL Linux home, not under /mnt" >&2
    exit 2
    ;;
esac

mkdir -p "$HOME/projects" "$HOME/Downloads"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
WORKSPACE="$HOME/projects/psych-design-release-proof-wsl-034-${STAMP}"
RECEIPT="$KIT_DIR/PSYCH_DESIGN_WSL_RELEASE_PROOF.json"
RUN_LOG="$KIT_DIR/PSYCH_DESIGN_WSL_RELEASE_PROOF.log"

if [[ -e "$WORKSPACE" || -e "$RECEIPT" || -e "$RUN_LOG" ]]; then
  echo "ERROR: refusing to reuse a WSL proof workspace or result file" >&2
  exit 2
fi

python3 run_psych_design_clean_reader_proof.py \
  --platform wsl \
  --wheel "./pystatsv1-0.26.0-py3-none-any.whl" \
  --workspace "$WORKSPACE" \
  --receipt "$RECEIPT" \
  --contract "./RELEASE_PROOF_CONTRACT.json" 2>&1 | tee "$RUN_LOG"

RESULT_ROOT="$KIT_DIR/.wsl-proof-result-${STAMP}"
mkdir "$RESULT_ROOT"
cp "$RECEIPT" "$RESULT_ROOT/"
cp "$RUN_LOG" "$RESULT_ROOT/"
cp RELEASE_PROOF_CONTRACT.json "$RESULT_ROOT/"
cp PSYCH_DESIGN_UBUNTU_RELEASE_PROOF.json "$RESULT_ROOT/"

python3 - "$RESULT_ROOT" <<'PY'
from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path
root=Path(sys.argv[1])
records=[]
for path in sorted(p for p in root.iterdir() if p.is_file()):
    records.append({'path':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
manifest={'schema_version':'pystatsv1-dropin-034-wsl-result-manifest-v0.1','files':records,'file_count':len(records)}
(root/'WSL_PROOF_RESULT_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
PY

RESULT_ZIP="$HOME/Downloads/pystatsv1-dropin-034-wsl-proof-result-${STAMP}.zip"
python3 - "$RESULT_ROOT" "$RESULT_ZIP" <<'PY'
from __future__ import annotations
import stat, sys, zipfile
from pathlib import Path
root=Path(sys.argv[1]); dest=Path(sys.argv[2])
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
    for path in sorted(p for p in root.iterdir() if p.is_file()):
        info=zipfile.ZipInfo(path.name,date_time=(1980,1,1,0,0,0))
        info.create_system=3
        info.external_attr=((stat.S_IFREG|0o644)&0xFFFF)<<16
        info.compress_type=zipfile.ZIP_DEFLATED
        zf.writestr(info,path.read_bytes())
PY

RESULT_SHA="$(sha256sum "$RESULT_ZIP" | awk '{print $1}')"
printf '%s  %s\n' "$RESULT_SHA" "$(basename "$RESULT_ZIP")" > "${RESULT_ZIP}.sha256"
rm -rf "$RESULT_ROOT"

printf '\nWSL proof result created:\n  %s\nSHA-256:\n  %s\n\n' "$RESULT_ZIP" "$RESULT_SHA"
echo "PYSTATSV1_DROPIN_034_WSL_PROOF_COMPLETE result=$RESULT_ZIP sha256=$RESULT_SHA"
