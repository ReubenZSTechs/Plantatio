#!/usr/bin/env bash
# Pull, build and restart.
set -euo pipefail
cd "$(dirname "$0")/../.."
docker compose pull
docker compose up -d --build
