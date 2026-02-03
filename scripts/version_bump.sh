#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/version_bump.sh <patch|minor|major|X.Y.Z>"
  exit 1
fi

python -m hatch version "$1"
