# AI FORMAT WORKSPACE

A modular AI project workspace template designed for:

- LLM systems
- RAG pipelines
- Multi-agent architectures
- Fine-tuning workflows
- Ollama deployment
- Evaluation pipelines
- Production deployment
- Research experimentation

---

# Project Structure

```text
AI FORMAT WORKSPACE/
│
├── backend/
├── frontend/
├── training/
├── deployment/
├── docs/
├── tests/
├── notebooks/
├── outputs/
├── logs/
├── models/
├── docker-compose.yaml
├── .env
├── .gitignore
├── LICENSE
└── README.md
```

---

# 1. Cara Menjalankan Aplikasi

## Prasyarat

Pastikan sudah terinstall:

- Python 3.10+
- pip
- Node.js & npm
- Git

---

## Langkah 1 — Clone Repository

```bash
git clone <url-repository-ini>
cd <nama-folder-repository>
```

---

## Langkah 2 — Menjalankan Backend

### 2.1 Masuk ke folder API

```bash
cd api
```

### 2.2 Buat dan aktifkan virtual environment

```bash
python -m venv venv
```

**Windows:**

```powershell
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

Kalau berhasil, prompt akan berubah menjadi `(venv)`.

### 2.3 Install dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Set PYTHONPATH ke root project

**Windows:**

```powershell
$env:PYTHONPATH = (Get-Item ..).FullName
```

**Mac/Linux:**

```bash
export PYTHONPATH=$(dirname $(pwd))
```

> Langkah ini wajib dilakukan agar Python bisa menemukan folder `backend/`.

### 2.5 Jalankan server

```bash
python main.py
```

Server akan berjalan di `http://localhost:8000`.

> **Catatan:** Saat pertama kali dijalankan, server akan otomatis mendownload model AI (~6.4GB). Pastikan koneksi internet stabil dan tunggu hingga selesai. Setelah terdownload, model tersimpan di cache dan tidak perlu download ulang.

### Dokumentasi API

Setelah server berjalan, buka browser dan akses:

```
http://localhost:8000/docs
```

### Catatan Penggunaan Ulang Backend

Untuk menjalankan server kembali setelah instalasi pertama, cukup:

```bash
cd api

# Aktifkan virtual environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Set PYTHONPATH
$env:PYTHONPATH = (Get-Item ..).FullName   # Windows
export PYTHONPATH=$(dirname $(pwd))        # Mac/Linux

python main.py
```

---

## Langkah 3 — Menjalankan Frontend

### 3.1 Buka terminal baru, lalu masuk ke folder frontend

```bash
cd frontend
```

### 3.2 Install dependencies (pertama kali saja)

```bash
npm install
```

### 3.3 Jalankan development server

```bash
npm run dev
```

Frontend akan berjalan di `http://localhost:8080`.

> **Catatan:** Pastikan backend sudah berjalan terlebih dahulu di `http://localhost:8000` sebelum membuka frontend.

### Catatan Penggunaan Ulang Frontend

Untuk menjalankan frontend kembali setelah instalasi pertama, cukup:

```bash
cd frontend
npm run dev
```

---

# 2. Folder Structure Explanation

## backend/

Main backend application.

Responsible for:

- API serving
- orchestration
- pipelines
- retrieval
- agent execution
- business logic
- observability
- model interaction

### backend/api/

FastAPI application layer.

Contains:

- routes
- middleware
- request schemas
- dependency injection
- API entrypoint

#### backend/api/main.py

Main FastAPI entrypoint.

Responsible for:

- initializing API
- registering routes
- middleware setup
- app startup

---

### backend/core/

Core infrastructure layer.

Contains:

- tracing
- streaming
- observability
- state management
- decorators
- graph execution

#### core/tracing/

Tracing execution across pipelines.

#### core/logging/

Central logging utilities.

#### core/graph/

Graph execution systems. Useful for:

- LangGraph
- DAG execution
- multi-agent workflow graphs

#### core/state/

Shared runtime state.

#### core/streaming/

Streaming token/output handling.

#### core/decorators/

Reusable decorators. Examples:

- retry
- timing
- logging
- caching

#### core/observability/

Monitoring utilities. Examples:

- metrics
- telemetry
- tracing
- performance tracking

---

### backend/services/

Business logic services.

#### llm_service.py

Handles:

- model inference
- Ollama requests
- prompt execution
- structured outputs

#### embedding_service.py

Embedding generation.

#### retrieval_service.py

Document retrieval orchestration.

#### routing_service.py

Intent routing and pipeline selection.

#### memory_service.py

Conversation memory management.

#### evaluation_service.py

Evaluation and scoring logic.

---

### backend/pipelines/

Pipeline execution layer.

#### pipelines/main/

Primary execution pipelines.

#### pipelines/rag/

RAG workflows.

#### pipelines/agents/

Agent orchestration.

#### pipelines/evaluation/

Evaluation pipelines.

---

### backend/retrieval/

Retrieval systems.

#### retrieval/vector/

Vector retrieval. Examples:

- ChromaDB
- FAISS
- Qdrant

#### retrieval/graph/

Graph retrieval. Examples:

- Neo4j
- knowledge graphs

#### retrieval/hybrid/

Hybrid retrieval. Combines:

- vector search
- keyword search
- graph retrieval

---

### backend/models/

Model abstractions.

#### models/llm/

LLM wrappers and configs.

#### models/embeddings/

Embedding model wrappers.

---

### backend/database/

Database integrations.

#### database/neo4j/

Neo4j graph database configuration.

---

### backend/configs/

Configuration layer.

#### configs/models/

Model YAML configurations.

#### configs/prompts/

Prompt templates.

#### configs/pipelines/

Pipeline definitions.

#### configs/logging/

Logging configuration.

---

## frontend/

Frontend application.

Responsible for:

- user interface
- dashboard
- interaction layer
- visualization

### frontend/main_app/

Main frontend source code.

#### components/

Reusable UI components.

#### pages/

Frontend pages/views.

#### services/

Frontend API communication.

#### utils/

Frontend utilities.

#### assets/

Static assets. Examples:

- images
- icons
- CSS

#### app.py

Frontend application entrypoint.

---

## training/

Training and fine-tuning system.

Responsible for:

- dataset preparation
- preprocessing
- LoRA training
- evaluation
- exporting
- GGUF conversion

### training/configs/

Training configuration files.

#### configs/models/

Model configs.

#### configs/lora/

LoRA configs.

#### configs/datasets/

Dataset configs.

---

### training/preprocessing/

Dataset preprocessing scripts.

#### clean_dataset.py

Dataset cleaning.

#### chunk_documents.py

Document chunking.

#### generate_qa_pairs.py

Generate synthetic QA data.

#### build_dataset.py

Final dataset formatting.

---

### training/scripts/

Training execution scripts. Examples:

- SFT
- PPO
- DPO
- evaluation
- exporting

---

### training/utils/

Training helper utilities. Examples:

- model loading
- GGUF conversion
- Ollama export
- dataset parsing

---

### training/datasets/

Dataset storage.

#### raw/

Raw unprocessed datasets.

#### processed/

Processed datasets.

#### formatted/

Instruction-formatted datasets.

#### evaluation/

Evaluation datasets.

---

### training/outputs/

Training outputs.

#### adapters/

LoRA adapters.

#### merged/

Merged full models.

#### gguf/

GGUF exported models.

#### checkpoints/

Training checkpoints.

#### runs/

Experiment runs.

#### metrics/

Training metrics.

#### logs/

Training logs.

---

## deployment/

Deployment infrastructure.

Responsible for:

- Docker
- Nginx
- Ollama deployment
- scripts
- production setup

### deployment/docker/

Dockerfiles:

- backend.Dockerfile
- frontend.Dockerfile
- nginx.Dockerfile
- ollama.Dockerfile

---

### deployment/nginx/

Nginx reverse proxy configuration.

#### nginx.conf

Main Nginx configuration.

---

### deployment/ngrok/

Ngrok exposure configuration.

#### ngrok.yaml

Ngrok configuration.

#### start_ngrok.sh

Launch ngrok tunnel.

---

### deployment/scripts/

Deployment automation scripts.

#### deploy.sh

Deploy services.

#### rebuild.sh

Rebuild containers.

#### start.sh

Start services.

#### stop.sh

Stop services.

---

## tests/

Testing infrastructure.

#### tests/api/

API tests.

#### tests/pipelines/

Pipeline tests.

#### tests/retrieval/

Retrieval tests.

#### tests/services/

Service tests.

#### tests/evaluation/

Evaluation tests.

#### tests/integration/

End-to-end integration tests.

---

## docs/

Project documentation.

#### architecture.md

System architecture.

#### pipeline.md

Pipeline explanation.

#### deployment.md

Deployment guide.

#### training.md

Training guide.

#### api.md

API documentation.

#### evaluation.md

Evaluation methodology.

#### observability.md

Monitoring and tracing.

---

## notebooks/

Jupyter notebooks. Used for:

- experimentation
- analysis
- debugging
- visualization

---

## outputs/

Generated outputs.

#### reports/

Generated reports.

#### analytics/

Analytics outputs.

#### exports/

Exported files.

#### generated_answer/

Generated responses.

#### benchmark_results/

Benchmark results.

---

## logs/

Runtime logs.

#### api/

API logs.

#### retrieval/

Retrieval logs.

#### llm/

LLM execution logs.

#### pipelines/

Pipeline logs.

#### evaluations/

Evaluation logs.

#### sessions/

Session logs.

#### traces/

Tracing logs.

#### errors/

Error logs.

#### archive/

Archived logs.

---

## models/

Local model storage. Examples:

- base models
- quantized models
- exported models
- GGUF models

---

## Root Files

### docker-compose.yaml

Main multi-container orchestration. Responsible for:

- backend
- frontend
- ollama
- databases
- nginx

### .env

Environment variables. Examples:

- API keys
- paths
- model names
- database credentials

### .gitignore

Defines files ignored by git. Examples:

- models
- checkpoints
- logs
- virtual environments
- datasets

### LICENSE

Project license.

### README.md

Project documentation.

---

# 3. Best Practices for Git Version Control

## Recommended Branch Strategy

```text
main
 ├── dev
 │    ├── feature/rag-pipeline
 │    ├── feature/multi-agent
 │    ├── feature/frontend
 │    ├── fix/retrieval-bug
 │    └── experiment/new-router
```

---

## Recommended Workflow

### main

Stable production-ready code.

### dev

Main development branch.

### feature/*

New features.

### fix/*

Bug fixes.

### experiment/*

Research or experimental features.

---

## Commit Best Practices

### Good Commit Examples

```bash
git commit -m "Add hybrid retrieval pipeline"
git commit -m "Fix ChromaDB metadata parsing"
git commit -m "Refactor agent orchestration service"
```

### Bad Commit Examples

```bash
git commit -m "update"
git commit -m "fix"
git commit -m "asdf"
```

---

# 4. Useful Git Commands

## Repository Initialization

```bash
git init
git clone <repository_url>
```

## Branching

```bash
git checkout -b feature/my-feature   # Create new branch
git checkout dev                     # Switch branch
git branch                           # List branches
```

## Staging and Commit

```bash
git status
git add .
git add backend/services/llm_service.py
git commit -m "Add intent routing service"
```

## Push and Pull

```bash
git push origin feature/my-feature
git pull origin dev
```

## Merge

```bash
git merge feature/my-feature
```

## Logs and History

```bash
git log
git log --oneline
```

## Undo Operations

```bash
git restore --staged <file>
git restore <file>
git reset --soft HEAD~1
```

## Stashing

```bash
git stash
git stash pop
```

## Remote Management

```bash
git remote add origin <repository_url>
git remote -v
```

---

# 5. Version Control Rules

**Rule 1 — Never commit:**

- datasets
- model weights
- checkpoints
- GGUF models
- secrets / API keys
- .env files
- logs

**Rule 2** — Always use branches. Do NOT develop directly on `main` or `production`.

**Rule 3** — Keep commits focused. One commit = one logical change.

**Rule 4** — Write meaningful commit messages.

**Rule 5** — Pull latest changes before pushing.

```bash
git pull origin dev
```

**Rule 6** — Use pull requests for major changes.

**Rule 7** — Tag stable releases.

```bash
git tag v1.0.0
```

**Rule 8** — Use `.gitignore` properly.

```gitignore
# Python
__pycache__/
*.pyc

# Virtual environments
venv/
.env/

# Models
models/
training/outputs/

# Logs
logs/

# Datasets
training/datasets/raw/

# Notebook checkpoints
.ipynb_checkpoints/
```

**Rule 9** — Separate experiments from production. Use `experiment/*` for research, temporary ideas, and unstable pipelines.

**Rule 10** — Document architectural changes. Whenever adding pipelines, changing orchestration, modifying retrieval, or introducing agents — update:

- `docs/architecture.md`
- `docs/pipeline.md`
- `README.md`

---

## Recommended Development Flow

```text
1. Create feature branch
2. Implement feature
3. Commit changes
4. Test locally
5. Push branch
6. Open pull request
7. Review and merge into dev
8. Merge dev into main after validation
```

---

# 6. Recommended AI Engineering Practices

## Separate Responsibilities

Avoid putting everything inside one file. Good separation:

- services
- pipelines
- retrieval
- prompts
- models
- configs
- deployment

## Keep YAML Configurable

Avoid hardcoding:

- model names
- paths
- prompts
- generation settings
- runtime configs

## Track Experiments

Always save:

- metrics
- prompts
- datasets
- configs
- model versions

## Use Structured Outputs

Prefer:

```json
{
  "answer": "..."
}
```

instead of raw text.

## Maintain Observability

Track:

- latency
- token usage
- retrieval quality
- hallucination rate
- routing decisions
- agent outputs

---

# Final Notes

This workspace template is designed to scale from:

- personal AI projects
- research projects
- RAG systems
- multi-agent systems
- enterprise AI applications
- production inference systems

The architecture intentionally separates:

- inference
- orchestration
- retrieval
- training
- deployment
- evaluation
- observability

so the system remains:

- modular
- maintainable
- scalable
- production-ready