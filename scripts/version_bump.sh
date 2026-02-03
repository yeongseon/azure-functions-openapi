#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/version_bump.sh <patch|minor|major|X.Y.Z>"
  exit 1
fi

script_dir="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "${script_dir}/.."

python -m hatch version "$1"
