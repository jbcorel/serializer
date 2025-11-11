import pytest

from serializer import Model, ValidationErrorGroup

class Profile(Model):
    name: str
    default_value: str = "default"

class User(Model):
    username: str
    email: str
    default_value: float = 35.8
    contact: Profile

class ProfileWithoutDefault(Model):
    name: str
    default_value: str

class UserWithoutDefault(Model):
    username: str
    email: str
    default_value: float
    contact: ProfileWithoutDefault



def test_valid_default_value():
    payload = {
        "username": "jbcorel",
        "email": "ddddd@mail.ru",
        "contact": {
            "name": "Max"
        }
    }

    result = User.validate(payload)
    assert result == {
        "username": "jbcorel",
        "email": "ddddd@mail.ru",
        "default_value": 35.8,
        "contact": {
            "name": "Max",
            "default_value": "default"
        }
    }


def test_without_default_value():
    payload = {
        "username": "jbcorel",
        "email": "ddddd@mail.ru",
        "contact": {
            "name": "Max"
        }
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        UserWithoutDefault.validate(payload)

    errors = excinfo.value.errors

    assert len(errors) == 2

    err_1 = errors[0]
    err_2 = errors[1]

    assert err_1["path"] == "default_value"
    assert err_1["message"] == "Отсутствует ключ default_value"
    assert err_1["value"] == "default_value"
    assert err_1["expected_type"] == "float"

    assert err_2["path"] == "contact.default_value"
    assert err_2["message"] == "Отсутствует ключ contact.default_value"
    assert err_2["value"] == "default_value"
    assert err_2["expected_type"] == "str"

    
