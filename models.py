# ==========================================
# БАЗОВЫЙ И ДОЧЕРНИЕ КЛАССЫ КОНТАКТОВ
# ==========================================

class Contact:
    """Базовый класс контакта."""
    extra_fields = ()
    validation_rules = {}  # Общие правила валидации (по умолчанию пустые)

    def __init__(self, name, phone, is_favorite=False, **kwargs):
        self.name = name
        self.phone = phone if isinstance(phone, list) else [phone]  # Поддержка нескольких телефонов
        self.is_favorite = is_favorite
        for field in self.extra_fields:
            setattr(self, field, kwargs.get(field))

    def matches(self, text):
        """Общая логика поиска."""
        text_lower = text.lower()
        phones_match = any(text_lower in str(p).lower() for p in self.phone)
        return text_lower in self.name.lower() or phones_match

    def validate(self):
        """Проверка без ветвления по типу."""
        for field, rule in self.validation_rules.items():
            value = getattr(self, field, None)
            if not rule(value):
                raise ValueError(f"Некорректное значение для поля '{field}': {value}")
        return True

    def display(self):
        fav_mark = " ★" if self.is_favorite else ""
        phones_str = ", ".join(self.phone)
        return f"{self.name}{fav_mark}\nТелефоны: {phones_str}"

    def summary(self):
        """Короткая строка для меню."""
        fav_mark = "★ " if self.is_favorite else ""
        phones_str = ", ".join(self.phone)
        return f"{fav_mark}{self.name} ({phones_str})"

    def to_dict(self):
        data = {
            "type": self.__class__.__name__,
            "name": self.name,
            "phone": self.phone,
            "is_favorite": self.is_favorite,
        }
        for field in self.extra_fields:
            data[field] = getattr(self, field, None)
        return data

    @classmethod
    def from_dict(cls, data):
        c_type = data.get("type", "Contact")
        name = data.get("name", "")
        phone = data.get("phone", "")
        is_favorite = data.get("is_favorite", False)

        target_cls = CONTACT_REGISTRY.get(c_type, {}).get("cls", Contact)
        kwargs = {}
        for field in target_cls.extra_fields:
            if field in data:
                kwargs[field] = data[field]

        instance = target_cls(name, phone, is_favorite=is_favorite, **kwargs)
        return instance


class PersonalContact(Contact):
    extra_fields = ("birthday",)
    validation_rules = {
        "birthday": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        fav_mark = " ★" if self.is_favorite else ""
        phones_str = ", ".join(self.phone)
        return f"{self.name}{fav_mark}\nТелефоны: {phones_str} | ДР: {self.birthday}"

    def summary(self):
        fav_mark = "★ " if self.is_favorite else ""
        return f"Личный | {fav_mark}{self.name} (ДР: {self.birthday})"


class WorkContact(Contact):
    extra_fields = ("company", "job_title")
    validation_rules = {
        "company": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        fav_mark = " ★" if self.is_favorite else ""
        phones_str = ", ".join(self.phone)
        return f"{self.name}{fav_mark}\nТелефоны: {phones_str} | {self.company}, {self.job_title}"

    def summary(self):
        fav_mark = "★ " if self.is_favorite else ""
        return f"Рабочий | {fav_mark}{self.name} ({self.company})"


class EmergencyContact(Contact):
    extra_fields = ("relationship", "priority")
    validation_rules = {
        "priority": lambda val: isinstance(val, bool)
    }

    def display(self):
        fav_mark = " ★" if self.is_favorite else ""
        status = "Срочный" if self.priority else "Обычный"
        phones_str = ", ".join(self.phone)
        return f"{self.name}{fav_mark}\nТелефоны: {phones_str} ({self.relationship}) [{status}]"

    def summary(self):
        fav_mark = "★ " if self.is_favorite else ""
        return f"Экстренный | {fav_mark}{self.name} ({self.relationship})"


class FamilyContact(Contact):
    extra_fields = ("family_role",)
    validation_rules = {
        "family_role": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        fav_mark = " ★" if self.is_favorite else ""
        phones_str = ", ".join(self.phone)
        return f"{self.name}{fav_mark}\nТелефоны: {phones_str} | Роль в семье: {self.family_role}"

    def summary(self):
        fav_mark = "★ " if self.is_favorite else ""
        return f"Семья | {fav_mark}{self.name} ({self.family_role})"


# ==========================================
# РЕЕСТР ТИПОВ (ФАБРИКА)
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