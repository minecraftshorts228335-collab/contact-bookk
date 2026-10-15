import json
import os

# Один смешанный список контактов (Требование 7)
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
        """Общий алгоритм валидации[cite: 11]."""
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

        subclasses = {
            "PersonalContact": PersonalContact,
            "WorkContact": WorkContact,
            "EmergencyContact": EmergencyContact,
            "Contact": Contact
        }

        target_cls = subclasses.get(c_type, Contact)
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
        """Требование 10: Возвращает строку сводки для личного контакта[cite: 10]."""
        return f"Личный: {self.name} (ДР: {self.birthday})"


class WorkContact(Contact):
    extra_fields = ("company", "job_title")
    validation_rules = {
        "company": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        return f"{self.name} - {self.phone} | {self.company}, {self.job_title}"

    def summary(self):
        """Требование 10: Возвращает строку сводки для рабочего контакта[cite: 10]."""
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
        """Требование 10: Возвращает строку сводки для экстренного контакта[cite: 10]."""
        return f"Экстренный: {self.name} ({self.relationship})"


# ==========================================
# ТРЕБОВАНИЕ 8: ОПЕРАЦИИ БЕЗ ПРОВЕРОК ТИПОВ
# ==========================================

def print_all(contacts_list):
    """Требование 8: Вызывает display() у каждого объекта без проверки типа[cite: 8]."""
    total_count = len(contacts_list)
    print(f"\n--- Общее количество контактов: {total_count} ---")
    if not contacts_list:
        print("Список контактов пуст.")
        return

    for index, contact in enumerate(contacts_list, start=1):
        print(f"{index}. {contact.display()}")
    print("-" * 45)


def search(contacts_list, text):
    """Требование 8: Вызывает matches(text) у каждого объекта и возвращает все совпадения без проверки типа[cite: 8]."""
    results = []
    for contact in contacts_list:
        if contact.matches(text):
            results.append(contact)
    return results


# ==========================================
# ТРЕБОВАНИЕ 10: МЕНЮ ВЫЗЫВАЕТ summary()
# ==========================================

def show_menu(contacts_list):
    """Требование 10: Меню вызывает summary() одинаковым способом для всех контактов[cite: 10]."""
    print(f"\n--- МЕНЮ КНИГИ КОНТАКТОВ (Всего: {len(contacts_list)}) ---")
    if not contacts_list:
        print("Список пуст.")
        return

    # Меню вызывает summary() одним и тем же способом, без выбора формата по типу[cite: 10]
    for number, contact in enumerate(contacts_list, start=1):
        print(f"{number}. {contact.summary()}")


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ИНТЕРФЕЙС
# ==========================================

def validate_phone(phone):
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) < 7:
        return False
    allowed_chars = set("0123456789+ -()")
    return all(char in allowed_chars for char in phone)


def add_contact():
    print("\nВыберите тип контакта:")
    print("1. Обычный контакт")
    print("2. Личный контакт (PersonalContact)")
    print("3. Рабочий контакт (WorkContact)")
    print("4. Экстренный контакт (EmergencyContact)")

    sub_choice = input("Ваш выбор (1-4): ").strip()
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
        if sub_choice == "2":
            birthday = input("Введите дату рождения: ").strip()
            new_contact = PersonalContact(name, phone, birthday=birthday)
        elif sub_choice == "3":
            company = input("Введите компанию: ").strip()
            job_title = input("Введите должность: ").strip()
            new_contact = WorkContact(name, phone, company=company, job_title=job_title)
        elif sub_choice == "4":
            relationship = input("Кем приходится: ").strip()
            priority_input = input("Высокий приоритет срочности? (да/нет): ").strip().lower()
            priority = priority_input in ("да", "д", "yes", "y")
            new_contact = EmergencyContact(name, phone, relationship=relationship, priority=priority)
        else:
            new_contact = Contact(name, phone)

        new_contact.validate()
        contacts.append(new_contact)
        print(f"Контакт '{name}' успешно добавлен!")
    except ValueError as e:
        print(f"Ошибка валидации: {e}")


def handle_search():
    query = input("Введите текст для поиска: ").strip()
    matched = search(contacts, query)  # Использует полиморфную функцию поиска (Требование 8)[cite: 8]

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
        print("1. Показать полный список (print_all)")
        print("2. Показать меню (summary)")
        print("3. Добавить контакт")
        print("4. Найти контакт (search)")
        print("5. Изменить контакт")
        print("6. Удалить контакт")
        print("7. Сохранить в файл")
        print("0. Выйти")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            print_all(contacts)  # Соответствует Требованию 8[cite: 8]
        elif choice == "2":
            show_menu(contacts)  # Соответствует Требованию 10[cite: 10]
        elif choice == "3":
            add_contact()
        elif choice == "4":
            handle_search()  # Соответствует Требованию 8[cite: 8]
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