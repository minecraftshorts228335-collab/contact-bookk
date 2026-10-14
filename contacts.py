import csv
import json
import os

# Глобальный список для хранения объектов контактов
contacts = []


# ==========================================
# КЛАСС КОНТАКТА
# ==========================================


class Contact:
  """Класс, описывающий отдельный контакт."""

  def __init__(self, name, phones, email, category):
    self.name = name  # Имя контакта
    self.phones = phones if isinstance(phones, list) else [phones]  # Список телефонов
    self.email = email  # Электронная почта
    self.category = category  # Категория (например, Семья, Работа)

  def to_dict(self):
    """Превращает объект контакта в словарь для сохранения в JSON."""
    return {
        "name": self.name,
        "phones": self.phones,
        "email": self.email,
        "category": self.category,
    }

  @classmethod
  def from_dict(cls, data):
    """Создает объект Contact из словаря при загрузке из файла."""
    # На случай старого формата, где был один телефон 'phone'
    phones = data.get("phones", [data.get("phone", "")])
    return cls(
        name=data.get("name", ""),
        phones=phones,
        email=data.get("email", ""),
        category=data.get("category", ""),
    )


# ==========================================
# ФУНКЦИИ ПРОВЕРКИ (ВАЛИДАЦИИ) ДАННЫХ
# ==========================================


def validate_phone(phone):
  """Проверка корректности телефона (не менее 7 цифр и допустимые символы)."""
  digits = "".join(filter(str.isdigit, phone))
  if len(digits) < 7:
    return False
  allowed_chars = set("0123456789+ -()")
  return all(char in allowed_chars for char in phone)


def validate_email(email):
  """Базовая проверка email (наличие '@' и точки в доменной части)."""
  if "@" not in email:
    return False
  parts = email.split("@")
  if len(parts) != 2 or not parts[0] or not parts[1]:
    return False
  return "." in parts[1]


# ==========================================
# ОСНОВНЫЕ ОПЕРАЦИИ С КОНТАКТАМИ
# ==========================================


def add_contact():
  """Добавление нового контакта с проверками."""
  name = input("Введите имя: ").strip()

  # Проверка уникальности имени (без учета регистра)
  for contact in contacts:
    if contact.name.strip().lower() == name.lower():
      print(f"Ошибка: контакт с именем '{name}' уже существует.")
      return

  # Ввод и проверка телефонов
  phones_raw = input("Введите телефоны через запятую: ").strip()
  split_phones = [p.strip() for p in phones_raw.split(",")]
  valid_phones = []

  for p in split_phones:
    if p and validate_phone(p):
      valid_phones.append(p)
    else:
      print(f"Пропущен некорректный телефон: {p}")

  if not valid_phones:
    print("Ошибка: у контакта должен быть хотя бы один корректный телефон.")
    return

  # Ввод и проверка email
  email = input("Введите email: ").strip()
  if not validate_email(email):
    print("Ошибка: некорректный формат email.")
    return

  category = input("Введите категорию (например, Семья, Работа): ").strip()

  # Создание объекта класса Contact и добавление в общий список
  new_contact = Contact(name, valid_phones, email, category)
  contacts.append(new_contact)
  print(f"Контакт '{name}' успешно добавлен!")


def show_all_contacts():
  """Вывод всего списка контактов и общего количества."""
  total_count = len(contacts)
  print(f"\n--- Общее количество контактов: {total_count} ---")
  if not contacts:
    print("Список контактов пуст.")
    return

  for index, contact in enumerate(contacts, start=1):
    phones_str = ", ".join(contact.phones)
    print(
        f"{index}. {contact.name} | Телефоны: [{phones_str}] | Email:"
        f" {contact.email} | Категория: {contact.category}"
    )
  print("-" * 45)


def search_contact():
  """Поиск контакта по имени или номеру телефона."""
  query = input("Введите имя или номер телефона для поиска: ").strip().lower()
  found = False

  print(f"\n--- Результаты поиска по запросу '{query}' ---")
  for contact in contacts:
    match_name = query in contact.name.lower()
    match_phone = any(query in p for p in contact.phones)

    if match_name or match_phone:
      phones_str = ", ".join(contact.phones)
      print(
          f"- {contact.name} | Телефоны: {phones_str} | Email:"
          f" {contact.email} | Категория: {contact.category}"
      )
      found = True

  if not found:
    print("Ничего не найдено.")


def update_contact():
  """Изменение существующего контакта по имени."""
  name_query = input(
      "Введите имя контакта, который нужно изменить: "
  ).strip().lower()

  matching = [c for c in contacts if name_query in c.name.lower()]

  if not matching:
    print(f"Контакты по запросу '{name_query}' не найдены.")
    return

  if len(matching) > 1:
    print("\nНайдено несколько контактов:")
    for i, c in enumerate(matching, start=1):
      print(f"{i}. {c.name}")
    print("Уточните имя для изменения.")
    return

  target = matching[0]
  print(
      f"Найден контакт: {target.name}. Оставьте поле пустым, чтобы не менять."
  )

  # 1. Изменение имени
  new_name = input(f"Новое имя [{target.name}]: ").strip()
  if new_name:
    exists = any(
        c != target and c.name.strip().lower() == new_name.lower()
        for c in contacts
    )
    if exists:
      print(
          f"Ошибка: контакт с именем '{new_name}' уже существует. Имя не"
          " изменено."
      )
    else:
      target.name = new_name

  # 2. Изменение телефонов
  current_phones = ", ".join(target.phones)
  new_phones_input = input(
      f"Новые телефоны через запятую [{current_phones}]: "
  ).strip()
  if new_phones_input:
    split_phones = [p.strip() for p in new_phones_input.split(",")]
    valid_new = [p for p in split_phones if validate_phone(p)]
    if valid_new:
      target.phones = valid_new
    else:
      print("Ошибка: не передано ни одного корректного телефона, старые сохранены.")

  # 3. Изменение email
  new_email = input(f"Новый email [{target.email}]: ").strip()
  if new_email:
    if validate_email(new_email):
      target.email = new_email
    else:
      print("Ошибка: неверный формат email, старый сохранен.")

  # 4. Изменение категории
  new_cat = input(f"Новая категория [{target.category}]: ").strip()
  if new_cat:
    target.category = new_cat

  print(f"Контакт '{target.name}' успешно обновлен!")


def delete_contact():
  """Удаление контакта по имени с подтверждением."""
  name_query = input("Введите имя контакта, который нужно удалить: ").strip().lower()

  matching = [c for c in contacts if name_query in c.name.lower()]

  if not matching:
    print(f"Контакты по запросу '{name_query}' не найдены.")
    return

  if len(matching) > 1:
    print("\nНайдено несколько контактов:")
    for i, c in enumerate(matching, start=1):
      print(f"{i}. {c.name}")
    print("Уточните имя для удаления.")
    return

  target = matching[0]
  phones_str = ", ".join(target.phones)
  print(
      f"Найден контакт: {target.name} (Телефоны: {phones_str}, Email:"
      f" {target.email})"
  )

  confirm = (
      input(f"Вы уверены, что хотите удалить '{target.name}'? (да/нет): ")
      .strip()
      .lower()
  )

  if confirm in ("да", "д", "yes", "y"):
    contacts.remove(target)
    print(f"Контакт '{target.name}' успешно удален.")
  else:
    print("Удаление отменено.")


# ==========================================
# ФУНКЦИИ РАБОТЫ С ФАЙЛАМИ
# ==========================================


def save_to_json(filename="contacts.json"):
  """Сохранение объектов контактов в JSON."""
  try:
    # Превращаем каждый объект Contact обратно в словарь с помощью метода to_dict()
    data = [c.to_dict() for c in contacts]
    with open(filename, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Контакты сохранены в файл '{filename}'.")
  except Exception as e:
    print(f"Ошибка сохранения: {e}")


def load_from_json(filename="contacts.json"):
  """Загрузка контактов из JSON с созданием объектов Contact."""
  global contacts
  if not os.path.exists(filename):
    print(f"Файл '{filename}' не найден, начинаем с пустого списка.")
    return

  try:
    with open(filename, "r", encoding="utf-8") as f:
      data = json.load(f)
      if isinstance(data, list):
        # Превращаем каждый элемент из файла в полноценный объект Contact
        contacts = [Contact.from_dict(item) for item in data]
        print(f"Загружено записей из файла: {len(contacts)}")
      else:
        print("Ошибка: неверный формат данных в файле.")
  except json.JSONDecodeError:
    print("Ошибка: файл поврежден (некорректный JSON).")
  except Exception as e:
    print(f"Ошибка загрузки: {e}")


# ==========================================
# ГЛАВНОЕ МЕНЮ ПРОГРАММЫ
# ==========================================


def main():
  load_from_json()  # Автозагрузка при старте

  while True:
    print("\n=== КНИГА КОНТАКТОВ ===")
    print("1. Показать список контактов")
    print("2. Добавить контакт")
    print("3. Найти контакт")
    print("4. Изменить контакт")
    print("5. Удалить контакт")
    print("6. Сохранить контакты в файл")
    print("0. Выйти из программы")

    choice = input("Выберите пункт меню: ").strip()

    if choice == "1":
      show_all_contacts()
    elif choice == "2":
      add_contact()
    elif choice == "3":
      search_contact()
    elif choice == "4":
      update_contact()
    elif choice == "5":
      delete_contact()
    elif choice == "6":
      save_to_json()
    elif choice == "0":
      save_to_json()  # Автосохранение перед выходом
      print("До свидания!")
      break
    else:
      print("Неверный выбор. Пожалуйста, введите число от 0 до 6.")


if __name__ == "__main__":
  main()