# PGR Mastering

## Dependencias

Base (obligatorias):
- Python deps en `requirements.txt`
- Sistema: `ffmpeg`, `libsndfile1`

IA Source Separation (opcional):
- `demucs` (en `requirements-ai.txt`)
- Se instala solo si activas build arg `ENABLE_AI_SEPARATION=1`

Run:
```bash
cp .env.example .env
mkdir -p data/uploads data/outputs data/jobs data/learning references
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d
```

### Build con separación IA real (Demucs)
```bash
docker compose build --no-cache --build-arg ENABLE_AI_SEPARATION=1
docker compose up -d
```

Checks:
```bash
docker compose ps
docker compose logs -f api
docker compose logs -f worker
curl http://127.0.0.1:${WEB_PORT:-8080}/api/health
curl http://127.0.0.1:${WEB_PORT:-8080}/api/plugins
curl http://127.0.0.1:${WEB_PORT:-8080}/api/learning
```

Optional free plugins:
```bash
./scripts/install_free_plugins_ubuntu.sh
./scripts/check_ffmpeg_plugins.sh
```
