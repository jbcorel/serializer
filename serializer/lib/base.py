from .ctx import ValidationContext
from .exc import ValidationError, ValidationErrorGroup
from .abstract import AbstractModel, AbstractSchemaValidator
from .schema_validator import SchemaValidator



class Model(AbstractModel):
    _validator_cls: type[AbstractSchemaValidator] = SchemaValidator

    @classmethod
    def _validate(cls, obj: dict, context: ValidationContext, coerce: bool = False) -> tuple[dict, list[ValidationError]]:
        if not isinstance(obj, dict):
            if context:
                context.add_error(
                    ValidationError(
                        path=context.path,
                        value=obj,
                        cause=f"Значение должно быть типа dict",
                        expected_type=cls.__name__,
                    )
                )
            return {}, []


        validator = cls._validator_cls(
            annotations=cls.__annotations__,
            default_values=cls._default_values,
            context=context,
            coerce=coerce
        )

        validated_obj = validator.validate_json(obj)

        return validated_obj, validator.ctx.errors
    

    @classmethod
    def validate(cls, obj: dict, *, coerce: bool = False) -> dict:
        if not isinstance(obj, dict):
            raise TypeError(f"Must be dict type, got {type(obj).__name__ }")
        
        validated_obj, errors = cls._validate(obj, ValidationContext(), coerce)

        if errors:
            raise ValidationErrorGroup(errors, cls.__name__)

        return validated_obj
        
    
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"Экземпляр класса '{cls.__name__}' не должен создаваться вручную, используйте метод {cls.__name__}.validate")