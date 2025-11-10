import pytest

from serializer import PhoneNumber

@pytest.mark.parametrize(
    "phone_number",
    (
        "7 (962) 292-11-48",
        "8 (962) 284-33-13",
        "7 (950) 222-33-44",
        "8 (921) 123-45-67",
        "8 (951) 234-34-32",
        "7 (123) 123-12-13",
        "8 (999) 999-99-99"
    )
)
def test_phone_number_valid(phone_number):
    ph_number = PhoneNumber(phone_number)

    assert isinstance(ph_number, str)
    assert ph_number.isdecimal()
    assert ph_number.startswith("7")


@pytest.mark.parametrize(
    "phone_number",
    (
        "4 (962) 292-11-48",
        "+7 (962) 284-33-13",
        "7 (95) 222-33-44",
        "8 (9211) 123-45-67",
        "8 (951) 23-343-32",
        "7 (123) 123-121-13",
        "8 (999) 999-99-993",
        "123456",
        "phone_number"
    )
)
def test_phone_number_invalid(phone_number):
    with pytest.raises(ValueError):
        PhoneNumber(phone_number)


def test_phone_number_conversion():
    assert PhoneNumber("8 (955) 318-99-12") == "79553189912"
    assert PhoneNumber("7 (999) 999-99-99") == "79999999999"