import pytest
from serializer import Model, ValidationErrorGroup


class Bar(Model):
    baz: str
    others: list[str]

class Foo(Model):
    bars: list[Bar]


def test_valid_annotation():
    valid_payload = {
        "bars": [
            {
                "baz": "test",
                "others": ["string", "string"]
            },
            {
                "baz": "test",
                "others": []
            }
        ]
    }

    result = Foo.validate(valid_payload)
    assert result == valid_payload 


def test_invalid_annotation():
    invalid_payload = {
        "bars": [
            {
                "baz": "test",
                "others": "string"
            },
            {
                "baz": "test",
                "others": 34.1
            }
        ]
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Foo.validate(invalid_payload)

    errors = excinfo.value.errors

    assert len(errors) == 2

    err_1 = errors[0]
    err_2 = errors[1]

    assert err_1["path"] == "bars.[0].others"
    assert err_1["message"] == "Тип контейнера str, ожидается list"
    assert err_1["value"] == "string"
    assert err_1["expected_type"] == "list"

    assert err_2["path"] == "bars.[1].others"
    assert err_2["message"] == "Тип контейнера float, ожидается list"
    assert err_2["value"] == 34.1
    assert err_2["expected_type"] == "list"
