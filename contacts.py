import csv
import json
import os


# ==========================================
# ПРОДВИНУТЫЙ УРОВЕНЬ: Класс Contact и Меню
# ==========================================


class Contact:
    """Класс для представления контакта с поддержкой нескольких телефонов."""

    def __init__(self, name, phones, email, category):
        self.name = name
        self.phones = phones if isinstance(phones, list) else [phones]
        self.email = email
        self.category = category

    def to_dict(self):
        """Преобразует объект в словарь для сохранения в JSON."""
        return {
            "name": self.name,
            "phones": self.phones,
            "email": self.email,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект Contact из словаря."""
        # Обратная совместимость, если в файле старый формат с одним 'phone'
        phones = data.get("phones", [data.get("phone", "")]
                          )
        return cls(
            name=data.get("name", ""),
            phones=phones,
            email=data.get("email", ""),
            category=data.get("category", ""),
        )


class ContactBook:
    """Класс для управления книгой контактов."""

    def __init__(self):
        self.contacts = []

    def validate_phone(self, phone):
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) < 7:
            return False
        allowed_chars = set("0123456789+ -()")
        return all(char in allowed_chars for char in phone)

    def validate_email(self, email):
        if "@" not in email:
            return False
        parts = email.split("@")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return False
        return "." in parts[1]

    def add_contact(self, name, phones, email, category):
        # Проверка уникальности имени (без учета регистра)
        for contact in self.contacts:
            if contact.name.lower() == name.lower():
                print(f"Ошибка: контакт с именем '{name}' уже существует.")
                return False

        # Проверка каждого телефона из списка
        validated_phones = []
        for p in phones:
            p_stripped = p.strip()
            if not p_stripped:
                continue
            if not self.validate_phone(p_stripped):
                print(f"Ошибка: некорректный формат телефона '{p_stripped}'.")
                return False
            validated_phones.append(p_stripped)

        if not validated_phones:
            print("Ошибка: у контакта должен быть хотя бы один номер телефона.")
            return False

        if not self.validate_email(email):
            print("Ошибка: некорректный формат email.")
            return False

        new_contact = Contact(name, validated_phones, email, category)
        self.contacts.append(new_contact)
        print(f"Контакт '{name}' успешно добавлен!")
        return True

    def show_all_contacts(self):
        total_count = len(self.contacts)
        print(f"\n--- Общее количество контактов: {total_count} ---")
        if not self.contacts:
            print("Список контактов пуст.")
            return

        for index, contact in enumerate(self.contacts, start=1):
            phones_str = ", ".join(contact.phones)
            print(
                f"{index}. {contact.name} | Телефоны: [{phones_str}] | Email:"
                f" {contact.email} | Категория: {contact.category}"
            )
        print("-" * 45)

    def search_contact(self, query):
        query_lower = query.lower()
        found = False
        print(f"\n--- Результаты поиска по запросу '{query}' ---")
        for contact in self.contacts:
            # Ищем по имени или по любому из телефонов
            match_name = query_lower in contact.name.lower()
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

    def delete_contact(self, name):
        initial_length = len(self.contacts)
        self.contacts = [
            c for c in self.contacts if c.name.lower() != name.lower()
        ]
        if len(self.contacts) < initial_length:
            print(f"Контакт '{name}' успешно удален.")
        else:
            print(f"Контакт с именем '{name}' не найден.")

    def update_contact(self, name):
        for contact in self.contacts:
            if contact.name.lower() == name.lower():
                print(f"Найден контакт: {contact.name}. Оставьте поле пустым, чтобы не менять.")

                current_phones = ", ".join(contact.phones)
                new_phones_input = input(f"Новые телефоны через запятую [{current_phones}]: ").strip()
                if new_phones_input:
                    split_phones = [p.strip() for p in new_phones_input.split(",")]
                    valid_new = []
                    for p in split_phones:
                        if self.validate_phone(p):
                            valid_new.append(p)
                        else:
                            print(f"Пропущен неверный номер: {p}")
                    if valid_new:
                        contact.phones = valid_new

                new_email = input(f"Новый email [{contact.email}]: ").strip()
                if new_email:
                    if self.validate_email(new_email):
                        contact.email = new_email
                    else:
                        print("Ошибка: неверный email, старый сохранен.")

                new_cat = input(f"Новая категория [{contact.category}]: ").strip()
                if new_cat:
                    contact.category = new_cat

                print("Контакт успешно обновлен!")
                return
        print(f"Контакт '{name}' не найден.")

    def save_to_json(self, filename="contacts.json"):
        try:
            data = [c.to_dict() for c in self.contacts]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Контакты сохранены в файл '{filename}'.")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def load_from_json(self, filename="contacts.json"):
        if not os.path.exists(filename):
            print(f"Файл '{filename}' не найден, начинаем с пустого списка.")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.contacts = [Contact.from_dict(item) for item in data]
                    print(f"Загружено записей из файла: {len(self.contacts)}")
                else:
                    print("Ошибка: неверный формат данных в файле.")
        except json.JSONDecodeError:
            print("Ошибка: файл поврежден (некорректный JSON).")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")


# ==========================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ==========================================
def main():
    book = ContactBook()
    book.load_from_json()  # Автозагрузка при старте

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
            book.show_all_contacts()
        elif choice == "2":
            name = input("Введите имя: ").strip()
            phones_raw = input("Введите телефоны через запятую: ").strip()
            phones = [p.strip() for p in phones_raw.split(",")]
            email = input("Введите email: ").strip()
            category = input("Введите категорию (например, Семья, Работа): ").strip()
            book.add_contact(name, phones, email, category)
        elif choice == "3":
            query = input("Введите имя или номер телефона для поиска: ").strip()
            book.search_contact(query)
        elif choice == "4":
            name = input("Введите имя контакта для изменения: ").strip()
            book.update_contact(name)
        elif choice == "5":
            name = input("Введите имя контакта для удаления: ").strip()
            book.delete_contact(name)
        elif choice == "6":
            book.save_to_json()
        elif choice == "0":
            book.save_to_json()  # Автосохранение перед выходом
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, введите число от 0 до 6.")


if __name__ == "__main__":
    main()