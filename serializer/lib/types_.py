import re

class PhoneNumber:
    _locale_pattern_map = {
        "ru": {
            "pattern": r"^[7|8]\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
            "begins": "7"
        } 
    }

    @classmethod
    def _build_number_str(cls, value: str, locale: str) -> str:
        return cls._locale_pattern_map[locale]["begins"] + "".join([c for c in value[1:] if c.isdecimal()])


    def __new__(cls, value: str, locale: str = "ru") -> str:
        if not isinstance(value, str):
            raise ValueError(f"Value {value} must conform to str type")
        
        if not re.fullmatch(cls._locale_pattern_map[locale]["pattern"], value):
            raise ValueError(f"Value {value} must conform to RU phone number format")
        
        return cls._build_number_str(value, locale)
    