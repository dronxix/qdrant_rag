from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from sentence_transformers import SentenceTransformer

# Объект схемы для тела запроса | Schema object for request body
class TextRequest(BaseModel):
    sentences: List[str]

# Инициализируем приложение FastAPI | Initialize FastAPI app
app = FastAPI()

# Загружаем модель для эмбеддингов | Load model for embeddings
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@app.post("/encode")
def encode_text(req: TextRequest):
    """
    Получаем эмбеддинги для списка предложений (sentences).
    Возвращаем массив числовых векторов. |
    Obtain embeddings for a list of sentences.
    Return an array of numeric vectors.
    """
    embeddings = model.encode(req.sentences)
    return {"embeddings": embeddings.tolist()}
