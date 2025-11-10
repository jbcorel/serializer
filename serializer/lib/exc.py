import json
from typing import Any


class ValidationError(Exception):
    def __init__(self, path: list[str], value: Any, cause: str, expected_type: type,  *args):
        self.path = path
        self.message = cause
        self.value = value
        self.expected_type = expected_type
        super().__init__(*args)
        
    def as_dict(self):
        return {
            "path": '.'.join(self.path),
            "message": self.message,
            "value": self.value,
            "expected_type": self.expected_type
        }


class ValidationErrorGroup(Exception):
    def __init__(self, errors: list[ValidationError], cls_name: str):
        self.errors = [error.as_dict() for error in errors]
        super().__init__(self.format_error_message(self.errors, cls_name))
    
    def format_error_message(self, errors_as_dict: list[dict], cls_name: str):
        err_count = len(errors_as_dict)
        msg = f"Got {err_count} validation errors for {cls_name}: \n\n"

        for err in errors_as_dict:
            msg += json.dumps(err, indent=4, ensure_ascii=False, separators=(",", ": "))
            msg += "\n\n"
        return msg
