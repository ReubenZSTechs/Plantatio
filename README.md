# AI Format Workspace

Template workspace modular untuk proyek AI — dirancang agar scalable dari eksperimen lokal hingga production.

**Cocok untuk:** LLM systems · RAG pipelines · Multi-agent architectures · Fine-tuning · Ollama deployment · Evaluation · Research

---

## Daftar Isi

- [Prasyarat](#prasyarat)
- [Struktur Proyek](#struktur-proyek)
- [Cara Menjalankan](#cara-menjalankan)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Menjalankan Backend](#2-menjalankan-backend)
  - [3. Menjalankan Frontend](#3-menjalankan-frontend)
- [Penjelasan Folder](#penjelasan-folder)
- [Catatan Arsitektur](#catatan-arsitektur)

---

## Prasyarat

Pastikan tools berikut sudah terinstall sebelum memulai:

| Tool | Versi Minimum |
|------|---------------|
| Python | 3.10+ |
| pip | terbaru |
| Node.js & npm | terbaru |
| Git | terbaru |

---

## Struktur Proyek

```
AI FORMAT WORKSPACE/
│
├── backend/                # API, services, pipelines, retrieval
├── frontend/               # UI dan dashboard
├── training/               # Fine-tuning dan dataset pipeline
├── deployment/             # Docker, Nginx, Ngrok, scripts
├── docs/                   # Dokumentasi teknis
├── tests/                  # Unit, integration, dan evaluation tests
├── notebooks/              # Jupyter notebooks untuk eksperimen
├── outputs/                # Hasil generate: laporan, analytics, benchmark
├── logs/                   # Runtime logs per komponen
├── models/                 # Penyimpanan model lokal
│
├── docker-compose.yaml     # Orkestrasi multi-container
├── .env                    # Environment variables
├── .gitignore
├── LICENSE
└── README.md
```

---

## Cara Menjalankan

### 1. Clone Repository

```bash
git clone <url-repository-ini>
cd <nama-folder-repository>
```

---

### 2. Menjalankan Backend

#### Langkah 2.1 — Masuk ke folder API

```bash
cd api
```

#### Langkah 2.2 — Buat virtual environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

Jika berhasil, prompt terminal akan berubah menjadi `(venv)`.

#### Langkah 2.3 — Install dependencies

```bash
pip install -r requirements.txt
```

#### Langkah 2.4 — Set PYTHONPATH

> **Wajib dilakukan** agar Python dapat menemukan folder `backend/`.

```bash
# Windows
$env:PYTHONPATH = (Get-Item ..).FullName

# Mac / Linux
export PYTHONPATH=$(dirname $(pwd))
```

#### Langkah 2.5 — Jalankan server

```bash
python main.py
```

Server berjalan di: **http://localhost:8000**

> **⚠️ Catatan — Download model pertama kali:**
> Server akan otomatis mengunduh model AI (>30 GB) saat pertama kali dijalankan.
> Pastikan koneksi internet stabil. Setelah terunduh, model tersimpan di cache dan tidak perlu diunduh ulang.
> Jika tidak memungkinkan, jalankan frontend saja tanpa backend

#### Dokumentasi API (Swagger UI)

Setelah server berjalan, buka:

```
http://localhost:8000/docs
```

#### Menjalankan ulang backend (setelah instalasi pertama)

```bash
cd api

# Aktifkan virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux

# Set PYTHONPATH
$env:PYTHONPATH = (Get-Item ..).FullName   # Windows
export PYTHONPATH=$(dirname $(pwd))        # Mac / Linux

python main.py
```

---

### 3. Menjalankan Frontend

> **Buka terminal baru** — pastikan backend sudah berjalan di `http://localhost:8000` sebelum memulai frontend.

#### Langkah 3.1 — Masuk ke folder frontend

```bash
cd frontend
```

#### Langkah 3.2 — Install dependencies (hanya pertama kali)

```bash
npm install
```

#### Langkah 3.3 — Jalankan development server

```bash
npm run dev
```

Frontend berjalan di: **http://localhost:8080**

#### Menjalankan ulang frontend (setelah instalasi pertama)

```bash
cd frontend
npm run dev
```

---

## Penjelasan Folder

### `backend/`

Layer utama aplikasi server. Menangani seluruh logika backend, mulai dari API hingga eksekusi pipeline.

```
backend/
├── api/            # FastAPI — routes, middleware, schemas, entrypoint (main.py)
├── core/           # Infrastruktur inti: tracing, logging, graph, state, streaming, decorators, observability
├── services/       # Business logic services
│   ├── llm_service.py          # Model inference & Ollama requests
│   ├── embedding_service.py    # Embedding generation
│   ├── retrieval_service.py    # Document retrieval orchestration
│   ├── routing_service.py      # Intent routing & pipeline selection
│   ├── memory_service.py       # Conversation memory
│   └── evaluation_service.py   # Evaluation & scoring
├── pipelines/      # Eksekusi pipeline: main, RAG, agents, evaluation
├── retrieval/      # Sistem retrieval: vector (ChromaDB/FAISS/Qdrant), graph (Neo4j), hybrid
├── models/         # Abstraksi model: LLM wrappers & embedding wrappers
├── database/       # Integrasi database (Neo4j)
└── configs/        # Konfigurasi YAML: models, prompts, pipelines, logging
```

---

### `frontend/`

Aplikasi antarmuka pengguna.

```
frontend/
└── main_app/
    ├── components/   # Reusable UI components
    ├── pages/        # Halaman / views
    ├── services/     # Komunikasi ke backend API
    ├── utils/        # Fungsi utilitas
    ├── assets/       # Gambar, ikon, CSS
    └── app.py        # Entrypoint frontend
```

---

### `training/`

Sistem fine-tuning dan manajemen dataset.

```
training/
├── configs/          # Konfigurasi: model, LoRA, dataset
├── preprocessing/    # Skrip preprocessing dataset
│   ├── clean_dataset.py        # Cleaning data
│   ├── chunk_documents.py      # Chunking dokumen
│   ├── generate_qa_pairs.py    # Generate data QA sintetis
│   └── build_dataset.py        # Format dataset final
├── scripts/          # Training scripts: SFT, PPO, DPO, evaluation, exporting
├── utils/            # Utilities: model loading, GGUF conversion, Ollama export
├── datasets/
│   ├── raw/          # Dataset mentah
│   ├── processed/    # Dataset yang sudah diproses
│   ├── formatted/    # Dataset berformat instruksi
│   └── evaluation/   # Dataset untuk evaluasi
└── outputs/
    ├── adapters/     # LoRA adapters
    ├── merged/       # Model hasil merge
    ├── gguf/         # Model format GGUF
    ├── checkpoints/  # Training checkpoints
    ├── runs/         # Experiment runs
    ├── metrics/      # Metrik training
    └── logs/         # Log training
```

---

### `deployment/`

Infrastruktur deployment dan orkestrasi container.

```
deployment/
├── docker/           # Dockerfiles: backend, frontend, nginx, ollama
├── nginx/            # Konfigurasi reverse proxy (nginx.conf)
├── ngrok/            # Konfigurasi tunnel publik (ngrok.yaml, start_ngrok.sh)
└── scripts/          # Skrip otomasi
    ├── deploy.sh     # Deploy semua services
    ├── rebuild.sh    # Rebuild containers
    ├── start.sh      # Start services
    └── stop.sh       # Stop services
```

---

### `tests/`

Infrastruktur testing.

```
tests/
├── api/          # API endpoint tests
├── pipelines/    # Pipeline tests
├── retrieval/    # Retrieval system tests
├── services/     # Service unit tests
├── evaluation/   # Evaluation tests
└── integration/  # End-to-end integration tests
```

---

### `docs/`

Dokumentasi teknis lengkap.

| File | Isi |
|------|-----|
| `architecture.md` | Arsitektur sistem |
| `pipeline.md` | Penjelasan pipeline |
| `deployment.md` | Panduan deployment |
| `training.md` | Panduan training |
| `api.md` | Dokumentasi API |
| `evaluation.md` | Metodologi evaluasi |
| `observability.md` | Monitoring & tracing |

---

### `notebooks/`

Jupyter notebooks untuk eksperimen, analisis, debugging, dan visualisasi.

---

### `outputs/`

Hasil generate dari sistem.

```
outputs/
├── reports/           # Laporan generate
├── analytics/         # Output analitik
├── exports/           # File ekspor
├── generated_answer/  # Respons yang dihasilkan
└── benchmark_results/ # Hasil benchmark
```

---

### `logs/`

Runtime logs per komponen.

```
logs/
├── api/         ├── retrieval/   ├── llm/
├── pipelines/   ├── evaluations/ ├── sessions/
├── traces/      ├── errors/      └── archive/
```

---

### `models/`

Penyimpanan model lokal: base models, quantized models, GGUF models, exported models.

---

### File Root

| File | Fungsi |
|------|--------|
| `docker-compose.yaml` | Orkestrasi container: backend, frontend, ollama, database, nginx |
| `.env` | Environment variables: API keys, paths, model names, credentials |
| `.gitignore` | Mengecualikan: models, checkpoints, logs, venv, datasets |
| `LICENSE` | Lisensi proyek |
| `README.md` | Dokumentasi ini |

---

## Catatan Arsitektur

Workspace ini dirancang untuk scale dari proyek personal hingga enterprise AI applications.

Arsitektur memisahkan komponen secara eksplisit:

```
inference  ·  orchestration  ·  retrieval
training   ·  deployment     ·  evaluation  ·  observability
```

Tujuannya agar sistem tetap **modular**, **maintainable**, **scalable**, dan **production-ready**.