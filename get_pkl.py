import pickle

def remove_prefix(text, prefix):
    """
    Удаляет префикс из строки, если он присутствует (без учёта регистра). |
    Removes a prefix from a string if it exists (case-insensitive).
    """
    if text.lower().startswith(prefix.lower()):
        return text[len(prefix):].strip()
    return text.strip()

def parse_text(text):
    """
    Функция принимает текст, где каждая пара вопрос-ответ (с опциональными скриншотами)
    разделена двойным переводом строки (\n\n). Внутри каждого блока:
      - Первая строка – вопрос (возможно, начинается с "Вопрос:").
      - Вторая строка – ответ (возможно, начинается с "Ответ:").
      - Дополнительные строки могут содержать скриншоты, например "Скриншот:", "Скриншот2:", "Скриншот3:".
      
    При добавлении в словарь из каждой строки удаляются указанные префиксы.

    |

    The function takes text where each question-answer pair (with optional screenshots)
    is separated by a double newline (\n\n). Within each block:
      - The first line is a question (possibly starting with "Вопрос:").
      - The second line is an answer (possibly starting with "Ответ:").
      - Additional lines may contain screenshots, e.g., "Скриншот:", "Скриншот2:", "Скриншот3:".
      
    When adding entries to the dictionary, specified prefixes are removed from each line.

    Возвращает список словарей, например: |
    Returns a list of dictionaries, for example:
      [
          {"вопрос": "Какой ваш вопрос?", "ответ": "Вот ответ", "скриншот": "3", "скриншот2": "4"},
          ...
      ]
    """
    # Разбиваем текст на блоки по двойному переводу строки | Split text into blocks by double newline
    blocks = text.strip().split("\n\n")
    result = []
    
    for block in blocks:
        # Разбиваем блок на строки | Split block into lines
        lines = block.strip().split("\n")
        # Если в блоке меньше двух строк, пропускаем его | Skip block if it has fewer than two lines
        if len(lines) < 2:
            continue
        
        # Удаляем префиксы "Вопрос:" и "Ответ:" для первой и второй строки соответственно |
        # Remove prefixes "Вопрос:" and "Ответ:" for the first and second lines, respectively
        question = remove_prefix(lines[0].strip(), "Вопрос: ")
        answer = remove_prefix(lines[1].strip(), "Ответ: ")
        entry = {"вопрос": question, "ответ": answer}
        
        # Обрабатываем дополнительные строки для скриншотов | Process additional lines for screenshots
        for line in lines[2:]:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            if line_lower.startswith("скриншот:"):
                value = remove_prefix(line_stripped, "Скриншот: ")
                entry["скриншот"] = value
            elif line_lower.startswith("скриншот2:"):
                value = remove_prefix(line_stripped, "Скриншот2: ")
                entry["скриншот2"] = value
            elif line_lower.startswith("скриншот3:"):
                value = remove_prefix(line_stripped, "Скриншот3: ")
                entry["скриншот3"] = value
            # Можно добавить дополнительные проверки для других вариантов скриншотов, если необходимо. |
            # Additional checks for other screenshot variants can be added if necessary.
        
        result.append(entry)
    
    return result

if __name__ == "__main__":
    # Чтение текста из файла "./result.txt" с кодировкой "utf-8" |
    # Reading text from the file "./result.txt" with encoding "utf-8"
    with open("./result.txt", "r", encoding="utf-8") as file:
        text = file.read()
    
    # Парсинг текста | Parsing the text
    parsed_data = parse_text(text)
    
    # Сохранение списка словарей в pkl файл | Saving the list of dictionaries to a pkl file
    with open("result.pkl", "wb") as file:
        pickle.dump(parsed_data, file)
    
    print("Данные успешно сохранены в файл data.pkl | Data successfully saved to file data.pkl")