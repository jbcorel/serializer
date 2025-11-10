import inspect
from abc import ABCMeta, abstractmethod, ABC
from typing import Any
from .exc import ValidationError


class MetaBase(type):
    def __new__(meta, name: str, bases: tuple, namespace: dict):
        cls = super().__new__(meta, name, bases, namespace)

        cls._default_values = {
            k: v
            for k, v in namespace.items()
            if not k.startswith("_") and not inspect.isroutine(v)
        }

        return cls


class ModelMeta(ABCMeta, MetaBase):
    pass
    

class AbstractModel(metaclass=ModelMeta):
    @classmethod
    @abstractmethod
    def _validate(cls, obj, context=None, coerce=False) -> tuple[dict, list[ValidationError]]:
        pass

    @classmethod
    @abstractmethod
    def validate(cls, obj: dict, *, coerce: bool) -> dict:
        pass


class AbstractSchemaValidator(ABC):    
    @abstractmethod
    def _coerce_value_to_type(self, value: Any, expected_type: Any):
        pass

    @abstractmethod
    def _check_without_coercion(self, value: Any, expected_type: Any):
        pass
        
    @abstractmethod
    def _process_list(self, lst: list, expected_type: Any) -> list[Any]:
        pass

    @abstractmethod
    def _validate_value_type(self, value: Any, expected_type: Any):
        pass

    @abstractmethod
    def validate_json(self, obj: dict) -> dict:
        pass