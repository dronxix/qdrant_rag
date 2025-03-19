# Телеграм-бот с системой RAG по конкретному файлу

## Описание

Данный репозиторий содержит инструкции и код для создания собственного Telegram-бота с системой Retrieval-Augmented Generation (RAG), позволяющей задавать вопросы и получать ответы на основе загруженных файлов. Вы можете загрузить несколько файлов и адаптировать код для поиска по множественным файлам.

---

## Структура проекта

### embed_server

Папка содержит Dockerfile для запуска сервера эмбеддингов, который генерирует эмбеддинги текста для последующего сохранения и поиска в векторной базе данных Qdrant.

Запускайте сервер эмбеддингов первым, следуя инструкции ниже.

### Важное замечание:

Во всех местах, где используется функция `load_dotenv()`, убедитесь, что в соответствующую папку положен файл `.env`, содержащий необходимые токены и ключи API. Необходимо установить dotenv и fitz для работы с документами (по мимо того, что есть в requirements.txt)

---

## Инструкция по запуску

### 1. Запуск Embed-сервера

Перейдите в папку `embed_server` и выполните:

```bash
docker build -t embed_server .
docker run -p 8080:8080 embed_server
```

### 2. Запуск Qdrant

```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

Для Windows используйте следующую команду (замените путь на ваш абсолютный путь):

```powershell
docker run -p 6333:6333 -p 6334:6334 -v C:\path\to\your\folder\qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 3. Формирование файла вопрос-ответ (`get_qua.py`)

Файл `get_qua.py` создаёт пары вопрос-ответ из вашего PDF-файла, сохраняя номера страниц с картинками. Проверяйте выходной файл на наличие лишних пробелов или неправильных разделений. Используется серверная модель LLM, но вы можете заменить её своей моделью (например, с помощью VLLM и OpenAI-запросов).

### 4. Создание файла pkl (`get_pkl.py`)

Файл `get_pkl.py` преобразует итоговый текстовый файл (`.txt`) в формат `.pkl`, упрощающий загрузку данных в Qdrant.

### 5. Загрузка в Qdrant (`load_to_qdrant.py`)

Файл `load_to_qdrant.py` загружает данные из pkl-файла в базу данных Qdrant.

### 6. Запуск Telegram-бота (`tg_bot.py`)

Файл `tg_bot.py` содержит код для работы Telegram-бота с системой RAG.

Сборка и запуск Telegram-бота:

```bash
docker build -t tg_bot .
docker run --network host -v $(pwd)/.env:/app/.env tg_bot
```

Для Windows используйте следующую команду (замените путь на ваш абсолютный путь):

```powershell
docker build -t tg_bot .
docker run --network host -v C:\path\to\your\folder\.env:/app/.env tg_bot
```

---

## English Version

# Telegram Bot with RAG System for Specific Files

## Description

This repository provides instructions and code for creating your own Telegram bot with a Retrieval-Augmented Generation (RAG) system, enabling question-answer functionality based on your uploaded files. You can upload multiple files and adapt the code for multi-file searches.

---

## Project Structure

### embed_server

Contains a Dockerfile for running the embeddings server, which generates text embeddings for storage and searching in the Qdrant vector database.

Start this server first according to the provided instructions.

### Important note:

Everywhere you use `load_dotenv()`, ensure that you place a `.env` file with necessary API keys and tokens in the respective folder. You need to install `dotenv` and `fitz` for document processing (in addition to what's listed in `requirements.txt`).

---

## Launch Instructions

### 1. Launching Embed Server

Navigate to `embed_server` directory and run:

```bash
docker build -t embed_server .
docker run -p 8080:8080 embed_server
```

### 2. Launching Qdrant

```bash
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

For Windows users, replace with your absolute path:

```powershell
docker run -p 6333:6333 -p 6334:6334 -v C:\path\to\your\folder\qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 3. Creating Question-Answer file (`get_qua.py`)

`get_qua.py` generates question-answer pairs from your PDF file, including page numbers for screenshots. Check the resulting file for unnecessary spaces or incorrect splits. The script uses an LLM model, but you can replace it with your own (e.g., VLLM with OpenAI).

### 4. Generating a pkl file (`get_pkl.py`)

`get_pkl.py` converts the resulting `.txt` file into a `.pkl` file for easier loading into Qdrant.

### 5. Loading data into Qdrant (`load_to_qdrant.py`)

`load_to_qdrant.py` uploads the question-answer data from the pkl file into the Qdrant database.

### 6. Launching the Telegram Bot (`tg_bot.py`)

`tg_bot.py` contains the Telegram bot functionality using the RAG system.

Build and run the Telegram bot:

```bash
docker build -t tg_bot .
docker run --network host -v $(pwd)/.env:/app/.env tg_bot
```

For Windows users, replace with your absolute path:

```powershell
docker build -t tg_bot .
docker run --network host -v C:\path\to\your\folder\.env:/app/.env tg_bot
```

---

**Now your Telegram bot with RAG functionality is ready to use!**
