# 1. Базовый уровень: список и основные операции

# Создаем пустой список контактов
contacts = []

# --- Добавление контактов ---
# Создаем первый контакт в виде словаря
contact1 = {
    "name": "Анна Петрова",
    "phone": "+7 900 123-45-67",
    "email": "anna@example.com",
    "category": "Друзья",
}

# Создаем еще несколько контактов для проверки
contact2 = {
    "name": "Иван Иванов",
    "phone": "+7 900 987-65-43",
    "email": "ivan@example.com",
    "category": "Работа",
}

contact3 = {
    "name": "Елена Смирнова",
    "phone": "+7 900 555-35-35",
    "email": "elena@example.com",
    "category": "Семья",
}

# Добавляем контакты в список
contacts.append(contact1)
contacts.append(contact2)
contacts.append(contact3)


# --- Функция для вывода всех контактов ---
def show_all_contacts():
  if not contacts:
    print("Список контактов пуст.")
    return

  print("\n--- Список контактов ---")
  for index, contact in enumerate(contacts, start=1):
    print(f"Запись №{index}")
    print(f"Имя: {contact['name']}")
    print(f"Телефон: {contact['phone']}")
    print(f"Email: {contact['email']}")
    print(f"Категория: {contact['category']}")
    print("-" * 20)


# --- Функция поиска по точному имени ---
def search_by_name(target_name):
  found = False
  for contact in contacts:
    if contact["name"].lower() == target_name.lower():
      print("\nКонтакт найден:")
      print(
          f"Имя: {contact['name']}, Телефон: {contact['phone']}, Email:"
          f" {contact['email']}, Категория: {contact['category']}"
      )
      found = True
      break
  if not found:
    print(f"\nКонтакт с именем '{target_name}' не найден.")


# --- Функция поиска по номеру телефона ---
def search_by_phone(target_phone):
  found = False
  for contact in contacts:
    if contact["phone"] == target_phone:
      print("\nКонтакт найден по телефону:")
      print(
          f"Имя: {contact['name']}, Телефон: {contact['phone']}, Email:"
          f" {contact['email']}, Категория: {contact['category']}"
      )
      found = True
      break
  if not found:
    print(f"\nКонтакт с номером '{target_phone}' не найден.")


# --- Функция удаления контакта по имени ---
def delete_contact(target_name):
  global contacts
  initial_length = len(contacts)
  contacts = [
      c for c in contacts if c["name"].lower() != target_name.lower()
  ]
  if len(contacts) < initial_length:
    print(f"\nКонтакт '{target_name}' успешно удален.")
  else:
    print(f"\nКонтакт '{target_name}' для удаления не найден.")


# --- Функция изменения контакта по имени ---
def update_contact(target_name):
  for contact in contacts:
    if contact["name"].lower() == target_name.lower():
      print(
          f"\nНайден контакт: {contact['name']}. Введите новые данные (оставьте"
          " поле пустым, чтобы не менять)."
      )

      new_phone = input(f"Новый телефон [{contact['phone']}]: ").strip()
      new_email = input(f"Новый email [{contact['email']}]: ").strip()
      new_category = input(f"Новая категория [{contact['category']}]: ").strip()

      if new_phone:
        contact["phone"] = new_phone
      if new_email:
        contact["email"] = new_email
      if new_category:
        contact["category"] = new_category

      print("Контакт успешно обновлен!")
      return

  print(f"\nКонтакт с именем '{target_name}' не найден.")


# --- Проверка работы базового уровня ---
if __name__ == "__main__":
  # 1. Показываем все добавленные контакты
  show_all_contacts()

  # 2. Проверяем поиск по имени
  search_by_name("Анна Петрова")

  # 3. Проверяем поиск по телефону
  search_by_phone("+7 900 987-65-43")

  # 4. Проверяем изменение контакта
  update_contact("Иван Иванов")

  # 5. Проверяем удаление контакта
  delete_contact("Елена Смирнова")

  # 6. Смотрим итоговый список
  show_all_contacts()

  # 2. Средний уровень: проверки, поиск по фрагменту, сортировка и категории

  contacts = []


  # --- Вспомогательные функции для проверки данных ---
  def validate_phone(phone):
      """Проверяет, что номер содержит достаточно цифр и допустимые символы."""
      # Оставляем только цифры для проверки их количества
      digits = "".join(filter(str.isdigit, phone))
      if len(digits) < 7:
          return False
      # Проверяем на допустимые символы (цифры, пробелы, плюсы, минусы, скобки)
      allowed_chars = set("0123456789+ -()")
      if not all(char in allowed_chars for char in phone):
          return False
      return True


  def validate_email(email):
      """Базовая проверка email: есть часть до и после '@', а после есть точка."""
      if "@" not in email:
          return False
      parts = email.split("@")
      # Убеждаемся, что до и после '@' есть непустые части, а в доменной части есть точка
      if len(parts) != 2 or not parts[0] or not parts[1]:
          return False
      if "." not in parts[1]:
          return False
      return True


  # --- Функция добавления контакта с проверками ---
  def add_contact(name, phone, email, category):
      # 1. Проверка уникальности имени (без учёта регистра: "Анна" и "анна" — одно и то же)[cite: 15]
      for contact in contacts:
          if contact["name"].lower() == name.lower():
              print(f"Ошибка: контакт с именем '{name}' уже существует.")
              return False

      # 2. Проверка телефона[cite: 13]
      if not validate_phone(phone):
          print(
              "Ошибка: некорректный формат телефона. Номер должен содержать не менее"
              " 7 цифр."
          )
          return False

      # 3. Проверка email[cite: 14]
      if not validate_email(email):
          print("Ошибка: некорректный формат email (пример: anna@example.com).")
          return False

      # Если всё успешно, создаем и добавляем контакт
      new_contact = {
          "name": name,
          "phone": phone,
          "email": email,
          "category": category,
      }
      contacts.append(new_contact)
      print(f"Контакт '{name}' успешно добавлен!")
      return True


  # --- Функция показа всех записей и общего количества ---
  def show_all_contacts():
      # Подсчёт общего количества записей[cite: 18]
      total_count = len(contacts)
      print(f"\n--- Общее количество контактов: {total_count} ---")

      if not contacts:
          print("Список контактов пуст.")
          return

      for index, contact in enumerate(contacts, start=1):
          print(
              f"{index}. {contact['name']} | Телефон: {contact['phone']} | Email:"
              f" {contact['email']} | Категория: {contact['category']}"
          )
      print("-" * 35)


  # --- Частичный поиск по имени[cite: 16] ---
  def search_partial_name(fragment):
      fragment_lower = fragment.lower()
      found_contacts = [
          c for c in contacts if fragment_lower in c["name"].lower()
      ]

      if found_contacts:
          print(f"\nРезультаты поиска по фрагменту '{fragment}':")
          for contact in found_contacts:
              print(
                  f"- {contact['name']} ({contact['phone']}), email:"
                  f" {contact['email']}, категория: {contact['category']}"
              )
      else:
          print(f"\nПо запросу '{fragment}' ничего не найдено.")


  # --- Сортировка по имени[cite: 17] ---
  def show_sorted_by_name():
      if not contacts:
          print("\nСписок пуст, сортировать нечего.")
          return

      # Сортируем копию списка по полю "name" (без учёта регистра)
      sorted_contacts = sorted(contacts, key=lambda x: x["name"].lower())

      print("\n--- Контакты, отсортированные по имени ---")
      for contact in sorted_contacts:
          print(f"{contact['name']} | {contact['phone']} | {contact['category']}")


  # --- Группировка по категориям[cite: 17] ---
  def show_by_categories():
      if not contacts:
          print("\nСписок пуст.")
          return

      # Собираем все уникальные категории
      categories = set(c["category"] for c in contacts)

      print("\n--- Группировка по категориям ---")
      for cat in sorted(categories):
          print(f"Категория: [{cat}]")
          cat_contacts = [c for c in contacts if c["category"] == cat]
          for contact in cat_contacts:
              print(f"  - {contact['name']} ({contact['phone']})")
      print("-" * 30)


  # --- Проверка работы среднего уровня ---
  if __name__ == "__main__":
      # 1. Проверяем валидацию и добавление
      add_contact(
          "Анна Петрова", "+7 900 123-45-67", "anna@example.com", "Друзья"
      )  # Успешно
      add_contact("Иван", "123", "ivan.example.com", "Работа")  # Ошибки валидации
      add_contact(
          "Иван Иванов", "+7 900 987-65-43", "ivan@example.com", "Работа"
      )  # Успешно
      add_contact("анна петрова", "+7 900 111-22-33", "anna2@example.com", "Семья")  # Ошибка: дубликат имени[cite: 15]
      add_contact(
          "Елена Смирнова", "+7 900 555-35-35", "elena@example.com", "Семья"
      )  # Успешно

      # 2. Вывод всех контактов и подсчёт[cite: 18]
      show_all_contacts()

      # 3. Проверка частичного поиска (например, ищем "ан")[cite: 16]
      search_partial_name("ан")

      # 4. Проверка сортировки по имени[cite: 17]
      show_sorted_by_name()

      # 5. Проверка группировки по категориям[cite: 17]
      show_by_categories()