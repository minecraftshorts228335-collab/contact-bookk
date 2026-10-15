import csv
import json
import os

# Глобальный список для хранения объектов контактов (один смешанный список)
contacts = []


# ==========================================
# БАЗОВЫЙ КЛАСС И ПОДКЛАССЫ КОНТАКТОВ
# ==========================================

class Contact:
    """Базовый класс, описывающий общий контакт."""
    extra_fields = ()
    validation_rules = {}

    def __init__(self, name, phones, email, **kwargs):
        self.name = name
        self.phones = phones if isinstance(phones, list) else [phones]
        self.email = email

        # Динамическое сохранение специфичных полей дочерних классов
        for field in self.extra_fields:
            setattr(self, field, kwargs.get(field))

    def matches(self, text):
        """Общая логика поиска по имени, номеру телефона или email."""
        text_lower = text.lower()
        match_name = text_lower in self.name.lower()
        match_phone = any(text_lower in p for p in self.phones)
        match_email = text_lower in self.email.lower()
        return match_name or match_phone or match_email

    def validate(self):
        """Общий алгоритм валидации по правилам validation_rules без ветвления по типам."""
        for field, rule in self.validation_rules.items():
            value = getattr(self, field)
            if not rule(value):
                raise ValueError(f"Некорректное значение для поля '{field}': {value}")
        return True

    def display(self):
        """Полное представление контакта."""
        phones_str = ", ".join(self.phones)
        return f"{self.name} | Телефоны: [{phones_str}] | Email: {self.email}"

    def summary(self):
        """Краткая строка для меню."""
        return f"{self.name} ({', '.join(self.phones)})"

    def to_dict(self):
        """Превращает объект в словарь для сохранения в JSON."""
        data = {
            "type": self.__class__.__name__,
            "name": self.name,
            "phones": self.phones,
            "email": self.email,
        }
        for field in self.extra_fields:
            data[field] = getattr(self, field, None)
        return data

    @classmethod
    def from_dict(cls, data):
        """Фабричный метод для создания объекта нужного подкласса при загрузке."""
        contact_type = data.get("type", "Contact")
        name = data.get("name", "")
        phones = data.get("phones", [data.get("phone", "")])
        email = data.get("email", "")

        # Фабрика распределяет по типам в зависимости от сохраненного класса
        if contact_type == "PersonalContact":
            return PersonalContact(name, phones, email, birthday=data.get("birthday", ""))
        elif contact_type == "WorkContact":
            return WorkContact(name, phones, email, company=data.get("company", ""),
                               job_title=data.get("job_title", ""))
        elif contact_type == "EmergencyContact":
            return EmergencyContact(name, phones, email, relationship=data.get("relationship", ""),
                                    priority=data.get("priority", False))
        else:
            return Contact(name, phones, email)


class PersonalContact(Contact):
    extra_fields = ("birthday",)
    validation_rules = {
        "birthday": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        phones_str = ", ".join(self.phones)
        return f"[Личный] {self.name} | Тел: [{phones_str}] | Email: {self.email} | ДР: {self.birthday}"

    def summary(self):
        return f"Личный: {self.name} (ДР: {self.birthday})"


class WorkContact(Contact):
    extra_fields = ("company", "job_title")
    validation_rules = {
        "company": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        phones_str = ", ".join(self.phones)
        return f"[Рабочий] {self.name} | Тел: [{phones_str}] | Email: {self.email} | {self.company} ({self.job_title})"

    def summary(self):
        return f"Рабочий: {self.name} — {self.company}"


class EmergencyContact(Contact):
    extra_fields = ("relationship", "priority")
    validation_rules = {
        "priority": lambda val: isinstance(val, bool)
    }

    def display(self):
        phones_str = ", ".join(self.phones)
        status = "Срочный" if self.priority else "Обычный"
        return f"[Экстренный] {self.name} | Тел: [{phones_str}] | Роль: {self.relationship} [{status}]"

    def summary(self):
        return f"Экстренный: {self.name} ({self.relationship})"


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
# ОСНОВНЫЕ ОПЕРАЦИИ С КОНТАКТАМИ (БЕЗ ПРОВЕРОК ТИПОВ)
# ==========================================

def add_contact():
    """Добавление нового контакта с выбором подтипа."""
    print("\nВыберите тип контакта:")
    print("1. Обычный / Базовый контакт")
    print("2. Личный контакт (PersonalContact)")
    print("3. Рабочий контакт (WorkContact)")
    print("4. Экстренный контакт (EmergencyContact)")

    sub_choice = input("Ваш выбор (1-4): ").strip()

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

    # Сбор специфичных полей в зависимости от выбора
    try:
        if sub_choice == "2":
            birthday = input("Введите дату рождения (например, 12.05): ").strip()
            new_contact = PersonalContact(name, valid_phones, email, birthday=birthday)
        elif sub_choice == "3":
            company = input("Введите компанию: ").strip()
            job_title = input("Введите должность: ").strip()
            new_contact = WorkContact(name, valid_phones, email, company=company, job_title=job_title)
        elif sub_choice == "4":
            relationship = input("Введите кем приходится (например, сестра): ").strip()
            priority_input = input("Высокий приоритет срочности? (да/нет): ").strip().lower()
            priority = priority_input in ("да", "д", "yes", "y")
            new_contact = EmergencyContact(name, valid_phones, email, relationship=relationship, priority=priority)
        else:
            new_contact = Contact(name, valid_phones, email)

        # Вызов общей валидации перед добавлением
        new_contact.validate()

        contacts.append(new_contact)
        print(f"Контакт '{name}' успешно добавлен!")
    except ValueError as e:
        print(f"Ошибка валидации: {e}")


def show_all_contacts():
    """Вывод всего списка контактов через полиморфный метод display()."""
    total_count = len(contacts)
    print(f"\n--- Общее количество контактов: {total_count} ---")
    if not contacts:
        print("Список контактов пуст.")
        return

    for index, contact in enumerate(contacts, start=1):
        # Используем общий полиморфный интерфейс display() без проверок типов
        print(f"{index}. {contact.display()}")
    print("-" * 45)


def search_contact():
    """Поиск контакта с использованием полиморфного метода matches()."""
    query = input("Введите текст для поиска (имя, телефон, email): ").strip()
    found = False

    print(f"\n--- Результаты поиска по запросу '{query}' ---")
    for contact in contacts:
        # Вызов метода matches() для каждого объекта независимо от его класса
        if contact.matches(query):
            print(f"- {contact.display()}")
            found = True

    if not found:
        print("Ничего не найдено.")


def update_contact():
    """Изменение существующего контакта по имени."""
    name_query = input("Введите имя контакта, который нужно изменить: ").strip().lower()

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
    print(f"Найден контакт: {target.name}. Оставьте поле пустым, чтобы не менять.")

    # 1. Изменение имени
    new_name = input(f"Новое имя [{target.name}]: ").strip()
    if new_name:
        exists = any(c != target and c.name.strip().lower() == new_name.lower() for c in contacts)
        if exists:
            print(f"Ошибка: контакт с именем '{new_name}' уже существует. Имя не изменено.")
        else:
            target.name = new_name

    # 2. Изменение телефонов
    current_phones = ", ".join(target.phones)
    new_phones_input = input(f"Новые телефоны через запятую [{current_phones}]: ").strip()
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

    # 4. Изменение специфичных полей в зависимости от доступных атрибутов объекта
    if hasattr(target, "birthday"):
        new_bday = input(f"Новая дата рождения [{target.birthday}]: ").strip()
        if new_bday:
            target.birthday = new_bday
    if hasattr(target, "company"):
        new_comp = input(f"Новая компания [{target.company}]: ").strip()
        if new_comp:
            target.company = new_comp
    if hasattr(target, "job_title"):
        new_job = input(f"Новая должность [{target.job_title}]: ").strip()
        if new_job:
            target.job_title = new_job
    if hasattr(target, "relationship"):
        new_rel = input(f"Новые отношения [{target.relationship}]: ").strip()
        if new_rel:
            target.relationship = new_rel

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
    print(f"Найден контакт: {target.summary()}")

    confirm = input(f"Вы уверены, что хотите удалить '{target.name}'? (да/нет): ").strip().lower()

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
        data = [c.to_dict() for c in contacts]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Контакты сохранены в файл '{filename}'.")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")


def load_from_json(filename="contacts.json"):
    """Загрузка контактов из JSON с восстановлением объектов нужных классов."""
    global contacts
    if not os.path.exists(filename):
        print(f"Файл '{filename}' не найден, начинаем с пустого списка.")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
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
    main()1