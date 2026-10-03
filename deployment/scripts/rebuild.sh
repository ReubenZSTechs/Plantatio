#!/usr/bin/env bash
# Rebuild images from scratch. Named volumes are preserved: passing -v here
# would silently destroy the knowledge graph.
set -euo pipefail
cd "$(dirname "$0")/../.."
docker compose down
docker compose build --no-cache
docker compose up -d
