# Video Downloader

Single-page web app: paste a video URL (TikTok, YouTube, Instagram, Facebook, etc.), get the file.

- Backend: FastAPI + [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Frontend: React (Vite)

## Quick start (local)

Requires Python 3.10+ and Node 18+.

```bash
./setup.sh   # one-time: creates venv, installs backend + frontend deps
./run.sh     # starts backend (8000) and frontend dev server (5173)
```

Open http://localhost:5173.

`run.sh` accepts `BACKEND_PORT` and `FRONTEND_PORT` env vars if you need different ports.

## Docker (deploy-ready)

Requires Docker and the Compose plugin.

```bash
docker compose up --build
```

Open http://localhost:8080. Override the host port with `PORT=80 docker compose up -d`.

The compose stack runs two services:

- `backend` — FastAPI + yt-dlp + ffmpeg, listening on `:8000` inside the network.
- `frontend` — Nginx serving the built React bundle and proxying `/api/*` to the backend.

For production, put a reverse proxy (Caddy, Traefik, or another Nginx) in front for TLS.

## Layout

```
backend/    FastAPI app, requirements, Dockerfile
frontend/   Vite + React app, Dockerfile (multi-stage → nginx), nginx.conf
setup.sh    one-shot local install
run.sh      start both servers locally
docker-compose.yml
```

## How it works

- Frontend POSTs `{ url }` to `/api/download`.
- Backend runs `yt-dlp` into a temp directory, then streams the file back with `Content-Disposition`.
- The temp file is deleted after the response finishes.

## Notes

- `ffmpeg` is included in the backend image so YouTube formats that need merging work out of the box. For local non-Docker runs, install ffmpeg system-wide if you want the same.
- Don't expose this publicly without rate-limiting and an allowlist — `yt-dlp` will happily fetch huge files for anyone who can reach the endpoint.
