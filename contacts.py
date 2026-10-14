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