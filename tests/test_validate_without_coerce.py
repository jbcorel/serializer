import pytest
from serializer import Model, PhoneNumber, ValidationErrorGroup


class PhoneWrapper(Model):
    phone: PhoneNumber

class User(Model):
    name: str
    phones: list[PhoneWrapper]

class Group(Model):
    group_name: str
    group_id: int
    members: list[User]

class Organization(Model):
    title: str
    groups: list[Group]

#----------------------------------------------

def test_model_valid():
    valid_group_payload = {
        "group_name": "FEIP",
        "group_id": 25,
        "members": []
    }

    result = Group.validate(valid_group_payload)

    assert result == valid_group_payload


def test_model_invalid():
    invalid_group_payload = {
        "group_name": 283,
        "group_id": 25,
        "members": []
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Group.validate(invalid_group_payload)

    err = excinfo.value.errors[0]

    assert err["path"] == "group_name"
    assert err["message"] == "Значение 283 не подходит к типу str"
    assert err["value"] == 283
    assert err["expected_type"] == 'str'
    

def test_nested_model_valid():
    valid_payload = {
        "title": "ACME Corp",
        "groups": [
            {
                "group_name": "Developers",
                "group_id": 12345678,
                "members": [
                    {
                        "name": "Alice",
                        "phones": [{"phone": "8 (950) 111-22-33"}],
                    },
                    {
                        "name": "Bob",
                        "phones": [{"phone": "7 (950) 333-44-55"}],
                    },
                ],
            }
        ],
    }
    
    result = Organization.validate(valid_payload, coerce=False)

    assert result == {
        "title": "ACME Corp",
        "groups": [
            {
                "group_name": "Developers",
                "group_id": 12345678,
                "members": [
                    {
                        "name": "Alice",
                        "phones": [{"phone": "79501112233"}],
                    },
                    {
                        "name": "Bob",
                        "phones": [{"phone": "79503334455"}],
                    },
                ],
            }
        ],
    }


def test_nested_model_invalid_list_element():
    invalid_payload = {
        "title": "ACME Corp",
        "groups": [
            {
                "group_name": "QA",
                "group_id": 12345678,
                "members": [
                    {
                        "name": "Charlie",
                        "phones": [
                            {"phone": "8 (950) 111-22-33"},
                            {"phone": "12345"},  # невалидный номер телефона
                        ],
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Organization.validate(invalid_payload)

    errors = excinfo.value.errors
    assert len(errors) == 1

    err = errors[0]

    assert err["path"] == 'groups.[0].members.[0].phones.[1].phone'
    assert err["message"] == 'Значение 12345 не подходит к типу PhoneNumber'
    assert err["value"] == '12345'
    assert err["expected_type"] == 'PhoneNumber'


def test_nested_model_invalid_value_type():
    invalid_payload = {
        "title": "ACME Corp",
        "groups": [
            {
                "group_name": "QA",
                "group_id": 12345678.01, #ожидается int, пришел float
                "members": [
                    {
                        "name": "Charlie",
                        "phones": [
                            {"phone": "8 (950) 111-22-33"},
                            {"phone": "8 (950) 111-22-33"},
                        ],
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Organization.validate(invalid_payload)

    errors = excinfo.value.errors
    assert len(errors) == 1

    err = errors[0]
    assert err["path"] == 'groups.[0].group_id'
    assert err["message"] == 'Значение 12345678.01 не подходит к типу int'
    assert err["value"] == 12345678.01
    assert err["expected_type"] == 'int'


def test_nested_model_multiple_errors():
    invalid_payload = {
        "title": "ACME Corp",
        "groups": [
            {
                "group_name": "QA",
                "group_id": 12345678.01, #ожидается int, пришел float
                "members": [
                    {
                        "name": "Charlie",
                        "phones": [
                            {"phone": "8 (950) 111-22-33"},
                            {"phone": "8 (950) 111-22-330"},  # невалидный номер телефона
                        ],
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Organization.validate(invalid_payload)

    errors = excinfo.value.errors

    assert len(errors) == 2

    err_invalid_type = errors[0]
    err_phone_number = errors[1]

    assert err_invalid_type["path"] == 'groups.[0].group_id'
    assert err_invalid_type["message"] == 'Значение 12345678.01 не подходит к типу int'
    assert err_invalid_type["value"] == 12345678.01
    assert err_invalid_type["expected_type"] == 'int'

    assert err_phone_number["path"] == 'groups.[0].members.[0].phones.[1].phone'
    assert err_phone_number["message"] == 'Значение 8 (950) 111-22-330 не подходит к типу PhoneNumber'
    assert err_phone_number["value"] == '8 (950) 111-22-330'
    assert err_phone_number["expected_type"] == 'PhoneNumber'