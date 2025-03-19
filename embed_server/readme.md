# Сервер для обработки эмбеддингов (RAG)

Репозиторий содержит исходный код сервера на FastAPI (`server.py`), предназначенного для обработки эмбеддингов в системах Retrieval-Augmented Generation (RAG).

## Как запустить сервер в Docker

### Сборка образа Docker

```bash
docker build -t fastapi-embed-server .
```

### Запуск Docker-контейнера

```bash
docker run -p 8080:8080 fastapi-embed-server
```

После запуска сервер доступен по адресу:
```
http://localhost:8080
```

---

# Embedding Processing Server (RAG)

This repository contains FastAPI server source code (`server.py`) for embedding processing within Retrieval-Augmented Generation (RAG) systems.

## How to Run Server with Docker

### Build Docker Image

```bash
docker build -t fastapi-embed-server .
```

### Run Docker Container

```bash
docker run -p 8080:8080 fastapi-embed-server
```

After running, the server will be available at:
```
http://localhost:8080
```