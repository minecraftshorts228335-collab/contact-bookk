import json
import os
from models import Contact

def validate_phone(phone):
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) < 7:
        return False
    allowed_chars = set("0123456789+ -()")
    return all(char in allowed_chars for char in phone)


def save_to_json(contacts_list, filename="contacts.json"):
    try:
        data = [c.to_dict() for c in contacts_list]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Контакты сохранены в файл '{filename}'.")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")


def load_from_json(filename="contacts.json"):
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                loaded_contacts = [Contact.from_dict(item) for item in data]
                print(f"Загружено записей из файла: {len(loaded_contacts)}")
                return loaded_contacts
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
    return []