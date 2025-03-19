import httpx
import asyncio
import json
from qdrant_client import QdrantClient
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI

# Импорт для конвертации страницы PDF в изображение | Import for converting PDF pages to images
from pdf2image import convert_from_path
import tempfile

load_dotenv()
BOT_TOKEN = os.getenv("CLS_BOT_TOKEN")  # Токен Telegram-бота | Telegram bot token
HYP_HB_API = os.getenv("HYP_HB_API")  # API-ключ Hyperbolic | Hyperbolic API key

client = AsyncOpenAI(
    base_url="https://api.hyperbolic.xyz/v1/",
    api_key=HYP_HB_API
)
# MODEL = 'Qwen/Qwen2.5-72B-Instruct'  # Альтернативная модель | Alternative model
MODEL = 'deepseek-ai/DeepSeek-V3'  # Используемая модель | Selected model

# Путь к PDF файлу  # Path to PDF file
PDF_FILE_PATH = os.path.abspath("./file.pdf")

# Создаем экземпляр бота и диспетчера | Create bot and dispatcher instances
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

FASTAPI_EMBED_URL = "http://127.0.0.1:8080/encode"  # URL для генерации эмбеддингов | Embedding generation endpoint
COLLECTION_NAME = "Client_bd"  # Название коллекции в Qdrant | Qdrant collection name
QDRANT_URL = "http://localhost:6333"  # URL Qdrant сервера | Qdrant server URL

qdrant_client = QdrantClient(url=QDRANT_URL)

async def rag(question: str):
    """
    Функция отправляет запрос на сервер для получения эмбеддингов,
    выполняет поиск в Qdrant и возвращает объединённый результат из 3 наиболее релевантных ответов.
    Также собирает номера страниц для возможных скриншотов.
    
    The function sends a request to the server to get embeddings,
    performs a Qdrant search, and returns a combined result from 3 most relevant answers.
    Also collects page numbers for potential screenshots.
    """
    payload = {"sentences": [question]}
    async with httpx.AsyncClient() as client_http:
        response = await client_http.post(
            FASTAPI_EMBED_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )

    if response.status_code != 200:
        raise Exception(f"Failed to get prediction: {response.status_code} {response.text}")

    embedding = json.loads(response.text)

    # Поиск по вектору: возвращаем 3 наиболее релевантных результата | Vector search: return 3 most relevant results
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding['embeddings'][0],
        limit=3,
        with_payload=True,
    )

    if not search_result:
        return None

    # Объединяем ответы в один текст | Combine answers into single text
    combined_answer = "\n".join([res.payload.get("answer", "") for res in search_result])
    # Собираем номера страниц из полей 'str' и 'str_2' | Collect page numbers from 'str' and 'str_2' fields
    pages_list = []
    for res in search_result:
        if res.payload.get("str"):
            pages_list.append(str(res.payload.get("str")))
        if res.payload.get("str_2"):
            pages_list.append(str(res.payload.get("str_2")))
    return {"answer": combined_answer, "pages": pages_list}

async def get_model_answer(question: str, answer_context: str, conversation_history: str):
    """
    Функция отправляет запрос к нейросетевой модели для получения полного ответа
    на основе вопроса, объединённого контекста из Qdrant и истории предыдущей переписки.
    
    The function sends a request to the neural network model to get a complete answer
    based on the question, combined context from Qdrant, and conversation history.
    """
    prompt = (f"Вопрос: {question}\n"
              f"Контекст: {answer_context}\n"
              f"История предыдущих вопросов и ответов:\n{conversation_history}\n"
              f"Пожалуйста, дай детальный ответ на вопрос, опираясь на контекст. "
              f"Возвращай только красиво оформленный ответ, используя пункты (1, 2, ...). "
              f"Ответ должен иметь вид 'Ответ:\nответ' без лишних заключительных фраз.")
    try:
        response = await client.completions.create(
            model=MODEL,
            prompt=prompt,
            temperature=0.0,
            stream=False  # Отключаем стриминг – получаем ответ целиком | Disable streaming - get full response
        )
        result_text = response.choices[0].text.strip()
        return result_text
    except Exception as e:
        raise Exception(f"Ошибка при получении ответа от нейросети: {e}")  # Error getting neural network response

def split_message(text: str, max_length: int = 4096):
    """
    Разбивает длинный текст на части не длиннее max_length символов.
    Splits long text into chunks not exceeding max_length characters.
    """
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

async def send_typing_action(chat_id: int, interval: int = 7):
    """
    Фоновая функция, которая периодически отправляет состояние "печатает" пользователю.
    Background function that periodically sends "typing" status to the user.
    """
    try:
        while True:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        return

# Создаем клавиатуру с единственной кнопкой "Получить pdf инструкцию" | Create keyboard with "Get PDF manual" button
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Получить pdf инструкцию")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start | /start command handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    intro_text = (
        "Привет! Я бот, который поможет найти ответ в инструкции клиентского сервиса! "
        "Задавай мне вопросы. У меня есть кнопка, которая вернёт всю инструкцию целиком."
    )
    await message.answer(intro_text, reply_markup=menu_keyboard)

# Обработчик команды /menu (при необходимости) | /menu command handler (if needed)
@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer("Меню:", reply_markup=menu_keyboard)

# Обработчик текстовых сообщений, отличных от кнопки "Получить pdf инструкцию" | Text message handler excluding PDF button
@dp.message(lambda message: message.text != "Получить pdf инструкцию")
async def handle_query(message: types.Message, state: FSMContext):
    user_query = message.text
    try:
        rag_result = await rag(user_query)
        if rag_result is None:
            await message.answer("Не найден релевантный ответ.")  # No relevant answer found
            return

        # Извлекаем объединённый контекст из Qdrant | Extract combined context from Qdrant
        qdrant_answer = rag_result.get("answer", "")
        pages_list = rag_result.get("pages", [])

        # Получаем историю переписки из состояния (если есть) | Get conversation history from state
        data = await state.get_data()
        history = data.get("history", [])
        history_text = ""
        for pair in history:
            history_text += f"Вопрос: {pair['user']}\nОтвет: {pair['bot']}\n"

        # Запускаем фоновую задачу для отправки состояния "печатает" | Start background typing indicator task
        typing_task = asyncio.create_task(send_typing_action(message.chat.id))
        # Получаем полный ответ от нейросети с учетом контекста и истории | Get full neural network response
        nn_response = await get_model_answer(user_query, qdrant_answer, history_text)
        # Останавливаем отправку состояния "печатает" | Stop typing indicator
        typing_task.cancel()

        # Если ответ длиннее лимита, разбиваем его на части | Split long responses into chunks
        for chunk in split_message(nn_response):
            await message.answer(chunk)

        # Выводим скриншоты страниц из PDF | Send PDF page screenshots
        for page in pages_list:
            try:
                page_number = int(page)
                images = convert_from_path(PDF_FILE_PATH, first_page=page_number, last_page=page_number)
                if images:
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                        images[0].save(tmp, format='JPEG')
                        tmp_path = tmp.name
                    await message.answer_photo(photo=FSInputFile(tmp_path), caption=f"Страница {page}")
                    os.remove(tmp_path)
                else:
                    await message.answer(f"Не удалось извлечь страницу {page} из PDF файла.")  # Failed to extract page
            except Exception as e:
                await message.answer(f"Ошибка при извлечении страницы {page}: {e}")  # Page extraction error

        # Обновляем историю переписки | Update conversation history
        history.append({"user": user_query, "bot": nn_response})
        if len(history) > 3:
            history = history[-3:]
        await state.update_data(history=history)

    except Exception as e:
        await message.answer(f"Произошла ошибка при выполнении запроса: {e}")  # Request execution error

# Обработчик кнопки "Получить pdf инструкцию" | PDF button handler
@dp.message(F.text == "Получить pdf инструкцию")
async def send_pdf(message: types.Message):
    try:
        pdf = FSInputFile(PDF_FILE_PATH)
        await message.answer_document(document=pdf)
    except Exception as e:
        await message.answer(f"Не удалось отправить PDF файл: {e}")  # Failed to send PDF

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())