#!/bin/bash
set -e

if [ "$1" = 'stitchee' ]; then
  exec uv run stitchee "$@"
elif [ "$1" = 'stitchee_harmony' ]; then
  exec uv run stitchee_harmony "$@"
else
  exec uv run stitchee_harmony "$@"
fi
