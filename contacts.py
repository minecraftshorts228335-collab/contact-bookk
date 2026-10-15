import json
import os

# Один смешанный список контактов (Требование 7)[cite: 7]
contacts = []


# ==========================================
# КЛАССЫ И ИНТЕРФЕЙС (Требования 1, 3, 4, 5)
# ==========================================

class Contact:
    extra_fields = ()
    validation_rules = {}

    def __init__(self, name, phone, **kwargs):
        self.name = name
        self.phone = phone
        for field in self.extra_fields:
            setattr(self, field, kwargs.get(field))

    def matches(self, text):
        """Общая логика поиска в базовом классе[cite: 4, 8]."""
        text_lower = text.lower()
        return text_lower in self.name.lower() or text_lower in str(self.phone).lower()

    def validate(self):
        """Требование 11: Общий алгоритм проверки данных без ветвления по типам[cite: 11]."""
        for field, rule in self.validation_rules.items():
            value = getattr(self, field, None)
            if not rule(value):
                raise ValueError(f"Некорректное значение для поля '{field}': {value}")
        return True

    def display(self):
        return f"{self.name} - {self.phone}"

    def summary(self):
        """Требование 10: Возвращает одну строку короткой сводки[cite: 10]."""
        return f"{self.name} ({self.phone})"

    def to_dict(self):
        data = {
            "type": self.__class__.__name__,
            "name": self.name,
            "phone": self.phone,
        }
        for field in self.extra_fields:
            data[field] = getattr(self, field, None)
        return data

    @classmethod
    def from_dict(cls, data):
        c_type = data.get("type", "Contact")
        name = data.get("name", "")
        phone = data.get("phone", "")

        target_cls = CONTACT_REGISTRY.get(c_type, {}).get("cls", Contact)
        kwargs = {}
        for field in target_cls.extra_fields:
            if field in data:
                kwargs[field] = data[field]
        return target_cls(name, phone, **kwargs)


class PersonalContact(Contact):
    extra_fields = ("birthday",)
    validation_rules = {
        "birthday": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        return f"{self.name} - {self.phone} ДР: {self.birthday}"

    def summary(self):
        return f"Личный: {self.name} (ДР: {self.birthday})"


class WorkContact(Contact):
    extra_fields = ("company", "job_title")
    validation_rules = {
        "company": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        return f"{self.name} - {self.phone} | {self.company}, {self.job_title}"

    def summary(self):
        return f"Рабочий: {self.name} ({self.company})"


class EmergencyContact(Contact):
    extra_fields = ("relationship", "priority")
    validation_rules = {
        "priority": lambda val: isinstance(val, bool)
    }

    def display(self):
        status = "Срочный" if self.priority else "Обычный"
        return f"{self.name} - {self.phone} ({self.relationship}) [{status}]"

    def summary(self):
        return f"Экстренный: {self.name} ({self.relationship})"


class FamilyContact(Contact):
    extra_fields = ("family_role",)
    validation_rules = {
        "family_role": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        return f"{self.name} - {self.phone} Роль в семье: {self.family_role}"

    def summary(self):
        return f"Семья: {self.name} ({self.family_role})"


# ==========================================
# РЕЕСТР ТИПОВ КОНТАКТОВ (Фабрика для расширения)
# ==========================================

CONTACT_REGISTRY = {
    "Contact": {
        "name": "Обычный контакт",
        "cls": Contact,
        "fields": []
    },
    "PersonalContact": {
        "name": "Личный контакт (PersonalContact)",
        "cls": PersonalContact,
        "fields": [("birthday", "Введите дату рождения: ")]
    },
    "WorkContact": {
        "name": "Рабочий контакт (WorkContact)",
        "cls": WorkContact,
        "fields": [("company", "Введите компанию: "), ("job_title", "Введите должность: ")]
    },
    "EmergencyContact": {
        "name": "Экстренный контакт (EmergencyContact)",
        "cls": EmergencyContact,
        "fields": [("relationship", "Кем приходится: "), ("priority", "Высокий приоритет срочности? (да/нет): ")]
    },
    "FamilyContact": {
        "name": "Семейный контакт (FamilyContact)",
        "cls": FamilyContact,
        "fields": [("family_role", "Введите роль в семье: ")]
    }
}


# ==========================================
# ТРЕБОВАНИЕ 8: ОПЕРАЦИИ БЕЗ ПРОВЕРОК ТИПОВ
# ==========================================

def print_all(contacts_list):
    """Вызывает display() у каждого объекта без проверки типа[cite: 8]."""
    total_count = len(contacts_list)
    print(f"\n--- Общее количество контактов: {total_count} ---")
    if not contacts_list:
        print("Список контактов пуст.")
        return

    for index, contact in enumerate(contacts_list, start=1):
        print(f"{index}. {contact.display()}")
    print("-" * 45)


def search(contacts_list, text):
    """Вызывает matches(text) у каждого объекта и возвращает все совпадения[cite: 8]."""
    results = []
    for contact in contacts_list:
        if contact.matches(text):
            results.append(contact)
    return results


# ==========================================
# ТРЕБОВАНИЕ 10 & 13: МЕНЮ И РЕЕСТР
# ==========================================

def show_menu(contacts_list):
    """Меню вызывает summary() одинаковым способом для всех контактов[cite: 10]."""
    print(f"\n--- МЕНЮ КНИГИ КОНТАКТОВ (Всего: {len(contacts_list)}) ---")
    if not contacts_list:
        print("Список пуст.")
        return

    for number, contact in enumerate(contacts_list, start=1):
        print(f"{number}. {contact.summary()}")


def add_contact():
    """Динамическое добавление через реестр типов без жесткого ветвления[cite: 13]."""
    print("\nВыберите тип контакта:")
    keys = list(CONTACT_REGISTRY.keys())
    for i, key in enumerate(keys, start=1):
        print(f"{i}. {CONTACT_REGISTRY[key]['name']}")

    choice_idx = input("Ваш выбор (номер): ").strip()
    if not choice_idx.isdigit() or not (1 <= int(choice_idx) <= len(keys)):
        print("Неверный выбор типа.")
        return

    selected_key = keys[int(choice_idx) - 1]
    type_info = CONTACT_REGISTRY[selected_key]

    name = input("Введите имя: ").strip()

    for contact in contacts:
        if contact.name.strip().lower() == name.lower():
            print(f"Ошибка: контакт с именем '{name}' уже существует.")
            return

    phone = input("Введите телефон: ").strip()
    if not validate_phone(phone):
        print("Ошибка: некорректный формат телефона.")
        return

    try:
        kwargs = {}
        for field, prompt in type_info["fields"]:
            val = input(prompt).strip()
            if field == "priority":
                kwargs[field] = val.lower() in ("да", "д", "yes", "y")
            else:
                kwargs[field] = val

        # Создание объекта через фабричный класс из реестра
        new_contact = type_info["cls"](name, phone, **kwargs)
        new_contact.validate()
        contacts.append(new_contact)
        print(f"Контакт '{name}' успешно добавлен!")
    except ValueError as e:
        print(f"Ошибка валидации: {e}")


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ИНТЕРФЕЙС
# ==========================================

def validate_phone(phone):
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) < 7:
        return False
    allowed_chars = set("0123456789+ -()")
    return all(char in allowed_chars for char in phone)


def handle_search():
    query = input("Введите текст для поиска: ").strip()
    matched = search(contacts, query)

    print(f"\n--- Результаты поиска по запросу '{query}' ---")
    if matched:
        for contact in matched:
            print(f"- {contact.display()}")
    else:
        print("Ничего не найдено.")


def update_contact():
    name_query = input("Введите имя контакта для изменения: ").strip().lower()
    matching = [c for c in contacts if name_query in c.name.lower()]

    if not matching:
        print(f"Контакты по запросу '{name_query}' не найдены.")
        return

    if len(matching) > 1:
        print("\nНайдено несколько контактов, уточните имя:")
        for i, c in enumerate(matching, start=1):
            print(f"{i}. {c.name}")
        return

    target = matching[0]
    print(f"Найден контакт: {target.name}. Оставьте поле пустым, чтобы не менять.")

    new_name = input(f"Новое имя [{target.name}]: ").strip()
    if new_name:
        target.name = new_name

    new_phone = input(f"Новый телефон [{target.phone}]: ").strip()
    if new_phone:
        if validate_phone(new_phone):
            target.phone = new_phone
        else:
            print("Ошибка: неверный формат телефона, старый сохранен.")

    for field in target.extra_fields:
        current_val = getattr(target, field)
        new_val = input(f"Новое значение для '{field}' [{current_val}]: ").strip()
        if new_val:
            if field == "priority":
                setattr(target, field, new_val.lower() in ("да", "д", "yes", "y"))
            else:
                setattr(target, field, new_val)

    print(f"Контакт '{target.name}' успешно обновлен!")


def delete_contact():
    name_query = input("Введите имя контакта для удаления: ").strip().lower()
    matching = [c for c in contacts if name_query in c.name.lower()]

    if not matching:
        print(f"Контакты не найдены.")
        return

    if len(matching) > 1:
        print("\nНайдено несколько контактов, уточните имя:")
        for i, c in enumerate(matching, start=1):
            print(f"{i}. {c.name}")
        return

    target = matching[0]
    confirm = input(f"Вы уверены, что хотите удалить '{target.name}'? (да/нет): ").strip().lower()
    if confirm in ("да", "д", "yes", "y"):
        contacts.remove(target)
        print(f"Контакт '{target.name}' удален.")
    else:
        print("Удаление отменено.")


def save_to_json(filename="contacts.json"):
    try:
        data = [c.to_dict() for c in contacts]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Контакты сохранены в файл '{filename}'.")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")


def load_from_json(filename="contacts.json"):
    global contacts
    if not os.path.exists(filename):
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                contacts = [Contact.from_dict(item) for item in data]
                print(f"Загружено записей из файла: {len(contacts)}")
    except Exception as e:
        print(f"Ошибка загрузки: {e}")


def main():
    load_from_json()

    while True:
        print("\n=== КНИГА КОНТАКТОВ ===")
        print("1. Показать список контактов (print_all)")
        print("2. Показать меню (summary)")
        print("3. Добавить контакт")
        print("4. Найти контакт (search)")
        print("5. Изменить контакт")
        print("6. Удалить контакт")
        print("7. Сохранить в файл")
        print("0. Выйти")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            print_all(contacts)
        elif choice == "2":
            show_menu(contacts)
        elif choice == "3":
            add_contact()
        elif choice == "4":
            handle_search()
        elif choice == "5":
            update_contact()
        elif choice == "6":
            delete_contact()
        elif choice == "7":
            save_to_json()
        elif choice == "0":
            save_to_json()
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Введите число от 0 до 7.")


if __name__ == "__main__":
    main()