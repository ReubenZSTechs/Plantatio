#!/usr/bin/env bash
# Build and start the full local stack.
set -euo pipefail
cd "$(dirname "$0")/../.."

[ -f .env ] || { echo "No .env found. Copy .env.example to .env first."; exit 1; }

docker compose up -d --build

echo "Web      http://localhost:8080"
echo "API      http://localhost:8000/docs"
echo "Neo4j    http://localhost:7474"
echo "Proxy    http://localhost"
