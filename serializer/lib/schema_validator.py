import typing
from typing import Any

from .abstract import AbstractModel
from .ctx import ValidationContext 
from .exc import ValidationError
from .abstract import AbstractSchemaValidator



class SchemaValidator(AbstractSchemaValidator):
    def __init__(self, annotations: dict, default_values: dict, context: ValidationContext, coerce: bool):
        self.annotations = annotations
        self.default_values = default_values
        self.coerce_flag = coerce
        self.ctx = ValidationContext.init_context(context)
            
    def _coerce_value_to_type(self, value, expected_type):
        try:
            return expected_type(value)
        except ValueError:
            self.ctx.add_error(
                ValidationError(
                    path=self.ctx.path, 
                    value=value,
                    cause=f"Значение {value} не может быть приведено к типу '{expected_type.__name__}'",
                    expected_type=expected_type.__name__,
                )
            )
            return


    def _check_without_coercion(self, value, expected_type) -> Any:
        init_type = type(value)
        try:
            coerced_value = expected_type(value)
        except (ValueError, ValidationError):
            self.ctx.add_error(
                ValidationError(
                    path=self.ctx.path, 
                    value=value,
                    cause=f"Значение {value} не подходит к типу {expected_type.__name__}",
                    expected_type=expected_type.__name__,
                )
            )
            return 
        else:
            if not isinstance(coerced_value, init_type):
                self.ctx.add_error(
                    ValidationError(
                        path=self.ctx.path, 
                        value=value,
                        cause=f"Значение {value} не подходит к типу {expected_type.__name__}",
                        expected_type=expected_type.__name__,
                    )
                )
                return 
            return coerced_value


    def _process_list(self, lst: list, expected_type: Any) -> list[Any]:
        validated_lst = []
        for idx, v in enumerate(lst):
            path_depth = self.ctx.depth
            self.ctx.append_path(str([idx]))
            validated_lst.append(self._validate_value_type(v, expected_type))
            self.ctx.remove_path_from_idx(path_depth)

        return validated_lst


    def _validate_value_type(self, value: Any, expected_type: Any):
        root = typing.get_origin(expected_type)
        args = typing.get_args(expected_type)

        if root:
            if type(value) != root:
                self.ctx.add_error(
                    ValidationError(
                        path=self.ctx.path, 
                        value=value,
                        cause=f"Тип контейнера {type(value).__name__}, ожидается {expected_type.__name__}",
                        expected_type=expected_type.__name__,
                    )
                )
                return
            
            return self._process_list(value, args[0])
        else:
            if issubclass(expected_type, AbstractModel):
                return expected_type._validate(value, context=self.ctx, coerce=self.coerce_flag)[0]
            
            if self.coerce_flag:
                return self._coerce_value_to_type(value, expected_type)
            else:
                return self._check_without_coercion(value, expected_type)


    def validate_json(self, obj: dict) -> dict:
        validated_obj = {}

        for key in self.annotations:
            path_depth = self.ctx.depth

            self.ctx.append_path(key)
            try:
                validated_obj[key] = self._validate_value_type(obj[key], self.annotations[key])
            except KeyError:
                if not self.default_values.get(key):
                    self.ctx.add_error(
                        ValidationError(
                            path=self.ctx.path, 
                            value=key,
                            cause=f"Отсутствует ключ {'.'.join(self.ctx.path)}",
                            expected_type=self.annotations[key].__name__,
                        )
                    )
                else:
                    validated_obj[key] = self.default_values[key]
            
            self.ctx.remove_path_from_idx(path_depth)

        return validated_obj