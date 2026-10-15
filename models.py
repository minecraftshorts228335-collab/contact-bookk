# ==========================================
# БАЗОВЫЙ И ДОЧЕРНИЕ КЛАССЫ КОНТАКТОВ
# ==========================================

class Contact:
    """Базовый класс контакта."""
    extra_fields = ()
    validation_rules = {}  # Общие правила валидации (по умолчанию пустые)

    def __init__(self, name, phone, **kwargs):
        self.name = name
        self.phone = phone
        for field in self.extra_fields:
            setattr(self, field, kwargs.get(field))

    def matches(self, text):
        """Общая логика поиска[cite: 4, 8]."""
        text_lower = text.lower()
        return text_lower in self.name.lower() or text_lower in str(self.phone).lower()

    def validate(self):
        """Проверка без ветвления по типу.
        Алгоритм перебирает правила и не сравнивает типы контактов[cite: 11]."""
        for field, rule in self.validation_rules.items():
            value = getattr(self, field, None)
            if not rule(value):
                raise ValueError(f"Некорректное значение для поля '{field}': {value}")
        return True

    def display(self):
        return f"{self.name}\n{self.phone}"

    def summary(self):
        """Короткая строка для меню[cite: 10]."""
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
        return f"{self.name}\n{self.phone} ДР: {self.birthday}"

    def summary(self):
        return f"Личный: {self.name} (ДР: {self.birthday})"


class WorkContact(Contact):
    extra_fields = ("company", "job_title")
    validation_rules = {
        "company": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        return f"{self.name}\n{self.phone} | {self.company}, {self.job_title}"

    def summary(self):
        return f"Рабочий: {self.name} ({self.company})"


class EmergencyContact(Contact):
    extra_fields = ("relationship", "priority")
    validation_rules = {
        "priority": lambda val: isinstance(val, bool)
    }

    def display(self):
        status = "Срочный" if self.priority else "Обычный"
        return f"{self.name}\n{self.phone} ({self.relationship}) [{status}]"

    def summary(self):
        return f"Экстренный: {self.name} ({self.relationship})"


class FamilyContact(Contact):
    """Четвёртый тип контакта с собственным полем family_role (Требование 14)[cite: 17]."""
    extra_fields = ("family_role",)
    validation_rules = {
        "family_role": lambda val: isinstance(val, str) and len(val.strip()) > 0
    }

    def display(self):
        return f"{self.name}\n{self.phone} Роль в семье: {self.family_role}"

    def summary(self):
        return f"Семья: {self.name} ({self.family_role})"


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