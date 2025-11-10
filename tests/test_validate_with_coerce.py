import pytest
from serializer import Model, PhoneNumber, ValidationErrorGroup


class Contact(Model):
    phone: PhoneNumber
    extension: int

class Employee(Model):
    first_name: str
    last_name: str
    contact: Contact

class Team(Model):
    team_name: str
    members: list[Employee]

class Department(Model):
    dept_name: str
    teams: list[Team]

class Company(Model):
    company_name: str
    departments: list[Department]

#-------------------------------------------

def test_employee_valid_coercion():
    valid_payload = {
        "first_name": "Max",
        "last_name": "Krivonosov",
        "contact": {
            "phone": "8 (960) 123-54-64",
            "extension": "22"
        }
    }

    result = Employee.validate(valid_payload, coerce=True)

    assert result == {
        "first_name": "Max",
        "last_name": "Krivonosov",
        "contact": {
            "phone": "79601235464",
            "extension": 22
        }
    }


def test_employee_invalid_coercion():
    invalid_payload = {
        "first_name": "Max",
        "last_name": "Krivonosov",
        "contact": {
            "phone": "8 (960) 123-54-64",
            "extension": "123абв"
        }
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Employee.validate(invalid_payload, coerce=True)

    errors = excinfo.value.errors
    assert len(errors) == 1
    err = errors[0]

    assert err["path"] == "contact.extension"
    assert err["message"] == "Значение 123абв не может быть приведено к типу 'int'"
    assert err["value"] == "123абв"
    assert err["expected_type"] == "int"


def test_company_valid_coercion():
    data = {
        "company_name": 12345,  # int -> str
        "departments": [
            {
                "dept_name": "Engineering",
                "teams": [
                    {
                        "team_name": "Backend",
                        "members": [
                            {
                                "first_name": "Alice",
                                "last_name": "Smith",
                                "contact": {
                                    "phone": "8 (950) 111-22-33",
                                    "extension": "101",  # str -> int
                                },
                            },
                            {
                                "first_name": "Bob",
                                "last_name": "Johnson",
                                "contact": {
                                    "phone": "7 (950) 222-33-44",
                                    "extension": 102,
                                },
                            },
                        ],
                    }
                ],
            }
        ],
    }

    result = Company.validate(data, coerce=True)

    assert result["company_name"] == "12345"
    contact_ext = result["departments"][0]["teams"][0]["members"][0]["contact"]["extension"]
    assert contact_ext == 101
    phone_num = result["departments"][0]["teams"][0]["members"][1]["contact"]["phone"]
    assert phone_num == "79502223344"


def test_company_invalid_coercion():
    data = {
        "company_name": "ACME Corp",
        "departments": [
            {
                "dept_name": "Engineering",
                "teams": [
                    {
                        "team_name": "Backend",
                        "members": [
                            {
                                "first_name": "Charlie",
                                "last_name": "Doe",
                                "contact": {
                                    "phone": "8 (950) 111-22-330",  # плохой формат
                                    "extension": "123АБВ",  # нельзя привести к int 
                                },
                            },
                            {
                                "first_name": "Dana",
                                "last_name": "White",
                                "contact": {
                                    "phone": 123456,  # плохой формат
                                    "extension": 103,
                                },
                            },
                        ],
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationErrorGroup) as excinfo:
        Company.validate(data, coerce=True)

    errors = excinfo.value.errors
    assert len(errors) == 3

    err_contact_phone_0 = errors[0]
    err_contact_extension_0 = errors[1]
    err_contact_phone_1 = errors[2]

    # Проверка ошибок
    assert err_contact_phone_0["path"] == "departments.[0].teams.[0].members.[0].contact.phone"
    assert err_contact_phone_0["message"] == "Значение 8 (950) 111-22-330 не может быть приведено к типу 'PhoneNumber'"
    assert err_contact_phone_0["value"] == "8 (950) 111-22-330"
    assert err_contact_phone_0["expected_type"] == "PhoneNumber"

    assert err_contact_extension_0["path"] == "departments.[0].teams.[0].members.[0].contact.extension"
    assert err_contact_extension_0["message"] == "Значение 123АБВ не может быть приведено к типу 'int'"
    assert err_contact_extension_0["value"] == "123АБВ"
    assert err_contact_extension_0["expected_type"] == "int"

    assert err_contact_phone_1["path"] == "departments.[0].teams.[0].members.[1].contact.phone"
    assert err_contact_phone_1["message"] == "Значение 123456 не может быть приведено к типу 'PhoneNumber'"
    assert err_contact_phone_1["value"] == 123456
    assert err_contact_phone_1["expected_type"] == "PhoneNumber"
    