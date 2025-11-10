# Serializer
Небольшая библиотека для валидации и нормализации JSON данных в Python.

---

## Основная идея

Библиотека позволяет описывать схемы данных через классы Python и валидировать JSON объекты в соответствии с этими схемами.  
Каждое поле класса проверяется на соответствие указанному типу, поддерживаются вложенные модели, списки и кастомные типы (например, `PhoneNumber`).  

---

## Установка и запуск тестов

> Пока библиотека используется локально, установка через uv.  
> Для тестов используется Docker. Чтобы запустить тесты: ```docker build -t serializer-tests -f test.Dockerfile . && docker run --rm serializer-tests```

---

## Использование

1. **Создание модели**

Чтобы определить класс для валидации JSON, нужно отнаследоваться от `Model`:

```python
from serializer import Model, PhoneNumber


class Contact(Model):
    phone: PhoneNumber
    extension: int

class Employee(Model):
    first_name: str
    last_name: str
    contact: Contact

data = {
    "first_name": "Alice",
    "last_name": "Smith",
    "contact": {
        "phone": "8 (950) 111-22-33",
        "extension": "101"  # можно передать строку, если coerce=True
    }
}

validated = Employee.validate(data)
```

При передаче флага coerce=True все вложенные поля, переданные в модель, будут приведены к аннотированному типу по возможности.

2. **Обработка ошибок**

Все ошибки валидации объединяются в **ValidationErrorGroup**.  
Это исключение содержит список всех ошибок, с указанием пути к полю, сообщения об ошибке и ожидаемого типа.
Строковое представление сообщения ошибки - JSON строка со списком объектов ошибок. Пример вывода:

```text
serializer.lib.exc.ValidationErrorGroup: Got 2 validation errors for Bar: 

    {
        "path": "baz",
        "message": "Отсутствует ключ baz",
        "value": "baz",
        "expected_type": "str"
    }

    {
        "path": "foo.bar",
        "message": "Значение 123абв не может быть приведено к типу 'int'"
        "value": "123абв",
        "expected_type": "int"
    }
```
### Пример использования

```python
from serializer import Model, PhoneNumber, ValidationErrorGroup


class Contact(Model):
    phone: PhoneNumber
    extension: int

data = {
    "phone": "8 (950) 111-22-330",  # неверный формат
    "extension": "NaN",              # нельзя привести к int
}

try:
    Contact.validate(data)
except ValidationErrorGroup as e:
    print(f"Найдено {len(e.errors)} ошибок:")
    for err in e.errors:
        print(f"Путь: {err['path']}")
        print(f"Сообщение: {err['message']}")
        print(f"Значение: {err['value']}")
        print(f"Ожидаемый тип: {err['expected_type']}")
        print("---")
```

