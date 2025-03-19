import requests 
import json 
import pickle 

COLLECTION_NAME = "Client_bd"  # Название базы данных | Database name
QDRANT_URL = "http://localhost:6333"  # Адрес Qdrant | Qdrant URL

# Функция создания коллекции в Qdrant | Function to create a collection in Qdrant
def create_collection():
    # Здесь задаём метрику и размерность | Here we define metric and dimensionality
    # delete_response = requests.delete(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")  # Если нужно удалить базу расскомментируйте | Uncomment to delete the collection if needed
    create_collection_payload = {
        "vectors": {
            "size": 384,  # Размерность вектора модели | Vector size of your model
            "distance": "Cosine"  # Метрика для расчета расстояний | Distance metric
        }
    }
    r = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(create_collection_payload)
    )
    if r.status_code == 200:
        print(f"Коллекция {COLLECTION_NAME} успешно создана (или уже существовала). | Collection {COLLECTION_NAME} created successfully (or already existed).")
    else:
        print("Ошибка при создании коллекции: | Error creating collection:", r.text)

FASTAPI_EMBED_URL = "http://127.0.0.1:8080/encode"  # Адрес сервиса для получения эмбеддингов | Embeddings service URL

# Функция для получения эмбеддингов | Function to get embeddings
def get_embeddings(sentences):
    """
    Обращаемся к нашему FastAPI сервису,
    передаём список строк, получаем массив эмбеддингов.

    |

    Send requests to our FastAPI service,
    pass a list of sentences, get an array of embeddings.
    """
    payload = {"sentences": sentences}
    r = requests.post(
        FASTAPI_EMBED_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    if r.status_code == 200:
        return r.json()["embeddings"]
    else:
        print("Ошибка при получении эмбеддингов: | Error retrieving embeddings:", r.text)
        return None

# Функция для вставки данных в Qdrant | Function to insert data into Qdrant
def insert_points_in_qdrant(vector, qw, ans, id, skr, skr_2):
    """
    vectors - список вектор вопроса | List of question vectors
    qw - вопрос | Question
    ans - ответ | Answer
    skr, skr_2 - скриншоты (необязательно, могут отсутствовать) | Screenshots (optional, can be omitted)
    """

    insert_payload = {
        "points": [
            {
                "id": id,
                "vector": vector,
                "payload": {
                    "question": qw,
                    "answer": ans,
                    "skr": skr,
                    "skr_2": skr_2
                }
            }
        ]
    }

    r = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points?wait=true",
        headers={"Content-Type": "application/json"},
        data=json.dumps(insert_payload)
    )
    if r.status_code == 200:
        print("Данные успешно вставлены в Qdrant. | Data successfully inserted into Qdrant.")
    else:
        print("Ошибка при вставке данных: | Error inserting data:", r.text)

# Тестовый пример | Test example
if __name__ == "__main__":
    create_collection()  # Создание коллекции при необходимости | Create collection if needed
    # Загружаем вопрос-ответ данные из файла | Load question-answer data from file
    with open('./result.pkl', 'rb') as f:
        qa_db = pickle.load(f)

    n = 0  # Счетчик поинтов | Points counter
    for m in qa_db:
        m_keys = list(m.keys())
        qw = m[m_keys[0]]
        ans = m[m_keys[1]]
        skr = None
        skr_2 = None
        if len(m_keys) > 2:
            skr = m[m_keys[2]]
            if len(m_keys) > 3:
                skr_2 = m[m_keys[3]]

        # Получаем эмбеддинги через FastAPI сервис | Get embeddings via FastAPI service
        embeddings = get_embeddings([qw])

        # Записываем эмбеддинги в Qdrant | Insert embeddings into Qdrant
        if embeddings:
            insert_points_in_qdrant(embeddings[0], qw, ans, n, skr, skr_2)
            n += 1

    print("Запись завершена | Writing completed")
