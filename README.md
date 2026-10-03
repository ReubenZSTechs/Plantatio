# Plantatio

AI growing intelligence for green produce, spanning two audiences: home
growers tending a few plants, and restoration operators managing land at
scale.

The system answers growing questions from a **knowledge graph** built out of
agronomy research, classifies **leaf disease** from a photograph, and scores
**satellite imagery** to find land worth restoring.

> Portfolio project. The architecture is real and runs end to end; the
> operational data is seeded demo content, and limitations are listed at the
> bottom rather than hidden.

---

## What it does

| | For growers (`/b2c`) | For enterprise (`/b2b`) |
|---|---|---|
| **Assistant** | Grounded answers about plant care, with the retrieved facts shown | Same graph, framed around operations |
| **Vision** | Photograph a leaf, get a ranked disease diagnosis | Satellite audit comparing a baseline and current image |
| **Monitoring** | Per-plant probe readings and a care timeline | Sensor fleet and restoration parcels on a live map |
| **Discovery** | — | Green Lands: candidate parcels ranked by restoration potential |

### How an answer is produced

```
Question
   │
   ├─ 1. Decompose      LLM splits the question into sub-questions
   │
   ├─ 2. Retrieve       each sub-question becomes Cypher, run against Neo4j
   │                    (schema injected into the prompt; keyword fallback
   │                     when the generated query returns nothing)
   │
   ├─ 3. Reason         step-by-step reasoning over the retrieved subgraph
   │
   └─ 4. Answer         grower-facing reply + the facts it came from
```

Orchestrated with LangGraph over a shared typed state. The retrieved facts are
returned to the UI, so every reply can be expanded to show its evidence — a
reply with nothing behind it says so rather than inventing support.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  React 19 · TanStack Start/Router · Tailwind v4 · shadcn/ui  │
│  /  ·  /b2c  ·  /garden/:id  ·  /b2b/{esg,green-lands,…}     │
└───────────────────────────┬──────────────────────────────────┘
                            │  VITE_API_BASE_URL
┌───────────────────────────▼──────────────────────────────────┐
│  FastAPI  ·  SQLAlchemy  ·  Pydantic v2                      │
│  plants · chat · diagnose · land-parcels · satellite         │
└───┬──────────────────┬──────────────────┬───────────────────-┘
    │                  │                  │
┌───▼──────────┐ ┌─────▼────────┐ ┌───────▼─────────┐
│ LangGraph    │ │ ResNet-50    │ │ Qwen2.5-VL      │
│ agent        │ │ leaf CNN     │ │ satellite VLM   │
└───┬──────────┘ └──────────────┘ └─────────────────┘
    │
┌───▼──────────────────┐   ┌──────────────────────┐
│ Neo4j knowledge graph│   │ Postgres / SQLite    │
│ 2,061 triplets       │   │ plants, parcels, logs│
└──────────────────────┘   └──────────────────────┘
```

### Tech stack

| Layer | Choice |
|---|---|
| Frontend | React 19, TanStack Start + Router (SSR), Tailwind CSS v4, shadcn/ui, TanStack Query |
| Map | Leaflet + react-leaflet over OpenStreetMap |
| API | FastAPI, Pydantic v2, SQLAlchemy 2 |
| Agent | LangGraph, HuggingFace Transformers |
| Knowledge graph | Neo4j, text-to-Cypher retrieval |
| Vision | PyTorch / torchvision (ResNet-50), Qwen2.5-VL via HF Inference |
| Database | Postgres in production, SQLite locally |

---

## Setup

### Prerequisites

Python 3.11+, Node 20+, and — optionally — Docker, a Neo4j instance, and a GPU
for the agent.

### 1. Configure

```bash
git clone <this-repo> && cd Plantatio
cp .env.example .env
```

Everything is read from `.env`. The app starts with none of it filled in; each
capability degrades with an explicit message rather than failing silently.

### 2. Backend

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r api/requirements.txt

export PYTHONPATH="$PWD:$PWD/api"                   # Windows: $env:PYTHONPATH="$PWD;$PWD\api"
uvicorn app.app:app --app-dir api --reload
```

API on <http://localhost:8000>, docs at `/docs`.

### 3. Frontend

```bash
npm install
npm run dev
```

### 4. Knowledge graph (optional but recommended)

Start Neo4j, put its credentials in `.env`, then load the graph:

```bash
python -m RAG.GRAPHRAG.src.pipeline.rag.neo4j_push
```

This ingests 2,061 subject–relation–object triplets extracted from 62 tomato
research papers, as 10 node labels (Disease, Pest, Nutrient, Symptom,
Solution and others) and 36 relationship types. Without it, retrieval returns
nothing and the assistant says so.

### 5. The agent's model

`PLANTATIO_LLM_MODEL_ID` defaults to `nvidia/Llama-3.1-8B-Instruct-NVFP4`.

> **NVFP4 needs NVIDIA Blackwell tensor cores** (RTX 50-series, B200). On older
> GPUs or CPU it will not load, and the chat endpoint returns a 503 naming the
> requirement. Point the variable at a model your hardware can run — for
> example `meta-llama/Llama-3.1-8B-Instruct` or `Qwen/Qwen2.5-7B-Instruct`.

One model instance serves all four roles (decomposition, text-to-Cypher,
reasoning, answering) with per-role decoding budgets, loaded on first use so
the API starts instantly.

### 6. Leaf classifier (optional)

Needs a trained checkpoint. See [`training/README.md`](training/README.md) for
the dataset layout and the two commands. Until one exists,
`POST /api/plants/{id}/diagnose` returns 503 pointing at those instructions —
it will not invent a diagnosis.

### Docker

```bash
cp .env.example .env
bash deployment/scripts/start.sh
```

Brings up the API, the built frontend, Neo4j with a persistent volume, and an
nginx proxy.

---

## What this demonstrates

- **Knowledge-graph construction** — 62 research papers reduced to 2,061 typed
  triplets, loaded as a labelled property graph with validated identifiers.
- **GraphRAG retrieval** — natural language to Cypher with the live schema
  injected into the prompt, LLM-output repair, an injected `LIMIT`, retry with
  backoff, and a keyword fallback when the generated query finds nothing.
- **Agent orchestration** — a four-node LangGraph pipeline over typed state,
  with retrieval provenance carried through to the UI.
- **Applied computer vision** — a ResNet-50 transfer-learning classifier with
  class-weighted loss for an imbalanced dataset, early stopping, and ROC/PR
  evaluation; plus a VLM scoring satellite imagery into comparable metrics.
- **Honest ML product design** — every model path degrades explicitly. No
  capability shows a fabricated result when its model is absent.
- **Full-stack delivery** — typed end to end, SSR frontend, containerised, with
  a test suite covering the contracts that previously broke silently.

---

## Project structure

```
api/                 FastAPI app: routes, schemas, ORM, configuration
backend/
  pipelines/         LangGraph agent, CNN inference, satellite VLM
  services/          vision diagnosis, land scoring, reference data
RAG/GRAPHRAG/        knowledge graph: text-to-Cypher, Neo4j, prompts
  tomat/             62 source research papers
src/                 React frontend
training/            CNN training and LLM fine-tuning pipelines
tests/               pytest suite
deployment/          Dockerfiles, nginx, scripts
```

---

## Testing

```bash
python -m pytest tests/ -q     # 44 tests
npx tsc --noEmit               # typecheck
npx eslint .                   # lint
npm run build                  # production build
```

The suite deliberately covers the seams that failed before: that the whole
import chain resolves, that the chat request contract is what the client
sends, that the agent runs end to end against injected fakes, that the
classifier's checkpoint round-trips, and that inference transforms are
deterministic.

---

## Limitations

Stated plainly, because a portfolio project that overclaims is worse than one
that does not.

- **Demo data is seeded.** Plants, sensors and land parcels are fixtures around
  one Jakarta site. Nothing is connected to real telemetry.
- **The EuroSAT reference labels are synthetic.** `misc/eurosat_vlm_labels.jsonl`
  was produced by prompting a model that had already been told each tile's
  class, so the labels are leaked and internally inconsistent. They populate
  the land-cover legend and tests only — nothing is mapped or measured from
  them, and the UI says so.
- **The satellite demo pair is not co-registered.** The 1986/2019 Landsat
  frames (via Google Earth Timelapse) are different crops of the same terrain,
  so the comparison is indicative rather than a pixel-level difference.
- **There is no authentication.** The enterprise console is open.
- **The knowledge graph covers tomato agronomy only.**
- **No leaf-classifier weights are distributed.** The architecture is a
  reconstruction against the training script's checkpoint contract, so a
  retrain is required.

## License

MIT — see [LICENSE](LICENSE).
