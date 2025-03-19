import fitz  
from openai import AsyncOpenAI  
import asyncio  
import traceback  
import os  
from dotenv import load_dotenv  # Для загрузки переменных среды | For loading environment variables

load_dotenv()

LLM_API = os.getenv("LLM_API")  # API ключ для доступа к LLM | API key for LLM access

# Инициализация асинхронного клиента OpenAI | Initializing asynchronous OpenAI client
client = AsyncOpenAI(
        base_url="https://api.hyperbolic.xyz/v1/",
        api_key=LLM_API
)

MODEL = 'Qwen/Qwen2.5-72B-Instruct'  # Название используемой LLM модели | Name of the LLM model

# Асинхронная функция для получения ответа от модели LLM | Asynchronous function to get response from LLM model
async def get_chatgpt_response(prompt) -> str:

    # Системное сообщение для задания роли помощника | System message to set assistant's role
    messages = [{"role": "system", "content": 'You are a Russian help assistant. Answer in Russian language only.'}]

    # Добавляем пользовательский промпт | Adding user prompt
    messages.append({"role": "user", "content": prompt})

    # Отправляем запрос и возвращаем ответ модели | Sending request and returning the model's response
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
        )
        print(response.usage)
        return response.choices[0].message.content
    except:
        print(traceback.format_exc())
        return ""

# Основная асинхронная функция | Main asynchronous function
async def main():
    pdf_path = os.path.abspath("./file.pdf")  # Путь до PDF-файла | Path to the PDF file
    docs = fitz.open(pdf_path)  # Открываем PDF-файл | Opening PDF file
    result_txt = ""
    result_llama_pdf_str = ""

    # Проходим по всем страницам PDF-файла | Iterate through all PDF pages
    for page_num in range(len(docs)):
        result_txt += f'Начало страницы {page_num + 1}'
        page = docs.load_page(page_num)  # Загружаем текущую страницу | Load current page
        text = page.get_text()  # Получаем текст со страницы | Get text from the page
        result_txt += text + "\n"
        images = page.get_images(full=True)  # Проверяем наличие изображений на странице | Check for images on the page

        # Если на странице есть изображения, добавляем соответствующее сообщение | If images exist, add a corresponding message
        if images:
            result_txt += f'На странице {page_num + 1} есть вспомогательные скриншоты'
        result_txt += f'Конец страницы {page_num + 1}'

        # Формируем промпт для LLM модели | Formulate prompt for LLM model
        # if any([page_num % 2, page_num == len(docs) - 1]):   # Если нужно сделать вопрос по тексту из двух страниц - раскомменте это и сдвиньте нижний блок
        prompt = ("""
                    Сделай вопросы и ответы на русском языке из предложенного текста, чтобы можно было это использовать для поиска в RAG. 
                    Выводи текстом Вопрос: вопрос Ответ: ответ, Вопрос: вопрос Ответ: ответ, Вопрос: вопрос Ответ: ответ.   
                    Если в тексте попадется 'На странице 2 есть вспомогательные скриншоты', то вывод по этой странице Вопрос: вопрос Ответ: ответ Скриншот: номер страницы.     
                    Текст: 
                    """ + result_txt
                  )
        """
        prompt = (Create questions and answers in Russian from the provided text, suitable for use in RAG search.
                    Output format: Question: question Answer: answer, Question: question Answer: answer, Question: question Answer: answer.
                    If the text contains 'На странице 2 есть вспомогательные скриншоты', include in the output for this page: Question: question Answer: answer Screenshot: page number.
                    Text:)
                    """

        # Получаем и сохраняем ответ от LLM модели | Get and save response from LLM model
        result_llama_pdf_str += await get_chatgpt_response(prompt)
        result_txt = ""

    # Записываем результат в файл | Write the result to a file
    with open('./result_2.txt', 'w', encoding='utf-8') as f:
        f.write(result_llama_pdf_str)

    print("Done")

# Запуск основной функции | Run the main function
if __name__ == '__main__':
    asyncio.run(main())
