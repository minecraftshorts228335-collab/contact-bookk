from models import Contact, CONTACT_REGISTRY
from utils import validate_phone, save_to_json, load_from_json

# Один смешанный список контактов[cite: 7, 14]
contacts = []


def print_all(contacts_list):
    """Вызывает display() у каждого объекта[cite: 8]."""
    total_count = len(contacts_list)
    print(f"\n--- Общее количество контактов: {total_count} ---")
    if not contacts_list:
        print("Список контактов пуст.")
        return

    for index, contact in enumerate(contacts_list, start=1):
        print(f"{index}. {contact.display()}")
    print("-" * 45)


def search(contacts_list, text):
    """Вызывает matches(text) у каждого объекта[cite: 8]."""
    results = []
    for contact in contacts_list:
        if contact.matches(text):
            results.append(contact)
    return results


def show_menu(contacts_list):
    """Меню вызывает summary() одинаковым способом[cite: 10]."""
    print(f"\n--- МЕНЮ КНИГИ КОНТАКТОВ (Всего: {len(contacts_list)}) ---")
    if not contacts_list:
        print("Список пуст.")
        return

    for number, contact in enumerate(contacts_list, start=1):
        print(f"{number}. {contact.summary()}")


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

        new_contact = type_info["cls"](name, phone, **kwargs)
        new_contact.validate()  # Вызов общего унаследованного validate()[cite: 11]

        contacts.append(new_contact)
        print(f"Контакт '{name}' успешно добавлен!")
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


def main():
    global contacts
    contacts = load_from_json()

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
            save_to_json(contacts)
        elif choice == "0":
            save_to_json(contacts)
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Введите число от 0 до 7.")


if __name__ == "__main__":
    main()