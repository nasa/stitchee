#!/bin/bash
set -e

if [ "$1" = 'stitchee' ]; then
  exec stitchee "$@"
elif [ "$1" = 'stitchee_harmony' ]; then
  exec stitchee_harmony "$@"
else
  exec stitchee_harmony "$@"
fi
