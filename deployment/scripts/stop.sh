#!/usr/bin/env bash
# Stop the stack, leaving the Neo4j volume intact.
set -euo pipefail
cd "$(dirname "$0")/../.."
docker compose down
