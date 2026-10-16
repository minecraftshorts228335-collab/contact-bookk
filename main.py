from models import Contact, CONTACT_REGISTRY
from utils import validate_phone, save_to_json, load_from_json

# Один смешанный список контактов
contacts = []


# ==========================================
# ПАТТЕРН КОМАНДА И МЕНЕДЖЕР ИСТОРИИ (UNDO / REDO)
# ==========================================

class Command:
    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


class HistoryManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def execute_command(self, command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # При новом действии очищаем стек повтора

    def undo(self):
        if not self.undo_stack:
            print("История отмен пуста.")
            return
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        print("Действие отменено.")

    def redo(self):
        if not self.redo_stack:
            print("История повторов пуста.")
            return
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        print("Действие повторено.")


history = HistoryManager()


class AddContactCommand(Command):
    def __init__(self, contacts_list, contact):
        self.contacts_list = contacts_list
        self.contact = contact

    def execute(self):
        self.contacts_list.append(self.contact)

    def undo(self):
        if self.contact in self.contacts_list:
            self.contacts_list.remove(self.contact)


class AddPhoneCommand(Command):
    def __init__(self, contact, phone):
        self.contact = contact
        self.phone = phone

    def execute(self):
        if self.phone not in self.contact.phone:
            self.contact.phone.append(self.phone)

    def undo(self):
        if self.phone in self.contact.phone:
            self.contact.phone.remove(self.phone)


class DeleteContactCommand(Command):
    def __init__(self, contacts_list, contact):
        self.contacts_list = contacts_list
        self.contact = contact
        self.index = contacts_list.index(contact) if contact in contacts_list else 0

    def execute(self):
        if self.contact in self.contacts_list:
            self.index = self.contacts_list.index(self.contact)
            self.contacts_list.remove(self.contact)

    def undo(self):
        self.contacts_list.insert(self.index, self.contact)


class EditContactCommand(Command):
    def __init__(self, contact, new_data):
        self.contact = contact
        self.new_data = new_data
        self.old_data = {}

    def execute(self):
        self.old_data = {
            "name": self.contact.name,
            "phone": list(self.contact.phone),
        }
        for field in self.contact.extra_fields:
            self.old_data[field] = getattr(self, field, None)

        if "name" in self.new_data:
            self.contact.name = self.new_data["name"]
        if "phone" in self.new_data:
            self.contact.phone = self.new_data["phone"]
        for field in self.contact.extra_fields:
            if field in self.new_data:
                setattr(self.contact, field, self.new_data[field])

    def undo(self):
        self.contact.name = self.old_data["name"]
        self.contact.phone = list(self.old_data["phone"])
        for field in self.contact.extra_fields:
            if field in self.old_data:
                setattr(self.contact, field, self.old_data[field])


class ToggleFavoriteCommand(Command):
    def __init__(self, contact):
        self.contact = contact
        self.old_status = contact.is_favorite

    def execute(self):
        self.old_status = self.contact.is_favorite
        self.contact.is_favorite = not self.old_status

    def undo(self):
        self.contact.is_favorite = self.old_status


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ОТОБРАЖЕНИЯ И СОРТИРОВКИ
# ==========================================

def get_sorted_contacts(contacts_list, sort_by="name"):
    """Сортирует контакты: избранные всегда сверху, внутри групп применяется выбранный порядок."""
    favorites = [c for c in contacts_list if c.is_favorite]
    others = [c for c in contacts_list if not c.is_favorite]

    if sort_by == "name":
        favorites.sort(key=lambda x: x.name.lower())
        others.sort(key=lambda x: x.name.lower())
    elif sort_by == "phone":
        favorites.sort(key=lambda x: x.phone[0] if x.phone else "")
        others.sort(key=lambda x: x.phone[0] if x.phone else "")

    return favorites + others


def print_all(contacts_list):
    """Вызывает display() у каждого объекта с учётом сортировки."""
    if not contacts_list:
        print("\nСписок контактов пуст.")
        return

    print("\nВыберите порядок сортировки для отображения:")
    print("1. По имени")
    print("2. По телефону")
    choice = input("Ваш выбор (1/2, по умолчанию по имени): ").strip()
    sort_key = "phone" if choice == "2" else "name"

    sorted_list = get_sorted_contacts(contacts_list, sort_key)
    print(f"\n--- Общее количество контактов: {len(sorted_list)} (Избранные сверху) ---")

    for index, contact in enumerate(sorted_list, start=1):
        print(f"{index}. {contact.display()}")
    print("-" * 45)


def search(contacts_list, text):
    results = []
    for contact in contacts_list:
        if contact.matches(text):
            results.append(contact)
    return results


def show_menu(contacts_list):
    """Меню вызывает summary() с учетом сортировки."""
    if not contacts_list:
        print("\nСписок пуст.")
        return

    sorted_list = get_sorted_contacts(contacts_list, "name")
    print(f"\n--- МЕНЮ КНИГИ КОНТАКТОВ (Всего: {len(sorted_list)}) ---")
    for number, contact in enumerate(sorted_list, start=1):
        print(f"{number}. {contact.summary()}")


# ==========================================
# ОСНОВНЫЕ ОПЕРАЦИИ МЕНЮ
# ==========================================

def add_contact():
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

    raw_name = input("Введите имя: ").strip()
    normalized_name = " ".join(raw_name.split()).lower()

    phone = input("Введите телефон: ").strip()
    if not validate_phone(phone):
        print("Ошибка: некорректный формат телефона.")
        return

    # Проверка совпадения имени (без учёта регистра и лишних пробелов)
    existing_contact = None
    for c in contacts:
        if " ".join(c.name.split()).lower() == normalized_name:
            existing_contact = c
            break

    if existing_contact:
        if phone in existing_contact.phone:
            print(ничто := f"Номер '{phone}' уже сохранен у контакта '{existing_contact.name}'.")
        else:
            cmd = AddPhoneCommand(existing_contact, phone)
            history.execute_command(cmd)
            print(f"Имя '{existing_contact.name}' уже существует. Новый номер успешно добавлен к нему!")
        return

    try:
        kwargs = {}
        for field, prompt in type_info["fields"]:
            val = input(prompt).strip()
            if field == "priority":
                kwargs[field] = val.lower() in ("да", "д", "yes", "y")
            else:
                kwargs[field] = val

        new_contact = type_info["cls"](raw_name, phone, **kwargs)
        new_contact.validate()

        cmd = AddContactCommand(contacts, new_contact)
        history.execute_command(cmd)
        print(f"Контакт '{raw_name}' успешно добавлен!")
    except ValueError as e:
        print(f"Ошибка валидации: {e}")


def handle_search():
    query = input("Введите текст для поиска: ").strip()
    matched = search(contacts, query)

    print(f"\n--- Результаты поиска по запросу '{query}' ---")
    if matched:
        for contact in matched:
            print(f"- {contact.display()}")
    else:
        print("Ничего не найдено.")


def toggle_favorite():
    name_query = input("Введите имя контакта для переключения статуса избранного: ").strip().lower()
    matching = [c for c in contacts if name_query in c.name.lower()]

    if not matching:
        print("Контакты не найдены.")
        return

    if len(matching) > 1:
        print("\nНайдено несколько контактов, уточните имя:")
        for i, c in enumerate(matching, start=1):
            print(f"{i}. {c.name}")
        return

    target = matching[0]
    cmd = ToggleFavoriteCommand(target)
    history.execute_command(cmd)
    status_text = "Избранный" if target.is_favorite else "Обычный"
    print(f"Статус контакта '{target.name}' изменен. Текущий статус: {status_text}.")


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

    new_data = {}
    new_name = input(f"Новое имя [{target.name}]: ").strip()
    if new_name:
        # Проверим, не занято ли имя другим контактом
        normalized_new = " ".join(new_name.split()).lower()
        if any(" ".join(c.name.split()).lower() == normalized_new and c != target for c in contacts):
            print("Ошибка: имя уже занято другим контактом.")
            return
        new_data["name"] = new_name

    new_phone = input(f"Новый основной телефон [{target.phone[0]}]: ").strip()
    if new_phone:
        if validate_phone(new_phone):
            updated_phones = list(target.phone)
            updated_phones[0] = new_phone
            new_data["phone"] = updated_phones
        else:
            print("Ошибка: неверный формат телефона, пропущено.")

    for field in target.extra_fields:
        current_val = getattr(target, field)
        new_val = input(f"Новое значение для '{field}' [{current_val}]: ").strip()
        if new_val:
            if field == "priority":
                new_data[field] = new_val.lower() in ("да", "д", "yes", "y")
            else:
                new_data[field] = new_val

    if new_data:
        cmd = EditContactCommand(target, new_data)
        history.execute_command(cmd)
        print(f"Контакт '{target.name}' успешно обновлен!")
    else:
        print("Изменения не внесены.")


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
        cmd = DeleteContactCommand(contacts, target)
        history.execute_command(cmd)
        print(f"Контакт '{target.name}' удален.")
    else:
        print("Удаление отменено.")


def main():
    global contacts
    contacts = load_from_json()

    while True:
        print("\n=== КНИГА КОНТАКТОВ ===")
        print("1. Показать список контактов (с сортировкой)")
        print("2. Показать меню (summary)")
        print("3. Добавить контакт (или номер, если имя совпало)")
        print("4. Найти контакт (search)")
        print("5. Изменить контакт")
        print("6. Удалить контакт")
        print("7. Добавить/убрать из избранного")
        print("8. Отменить последнее действие (Undo)")
        print("9. Повторить отмененное действие (Redo)")
        print("10. Сохранить в файл")
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
            toggle_favorite()
        elif choice == "8":
            history.undo()
        elif choice == "9":
            history.redo()
        elif choice == "10":
            save_to_json(contacts)
        elif choice == "0":
            save_to_json(contacts)
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Введите число от 0 до 10.")


if __name__ == "__main__":
    main()