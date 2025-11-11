from typing import Self

from .exc import ValidationError


class ValidationContext:
    def __init__(self):
        self._errors: list[ValidationError] = []
        self._path_stack = []

    def append_path(self, path: str):
        self._path_stack.append(path)
    
    def remove_path_from_idx(self, idx: int):
        self._path_stack = self._path_stack[:idx]

    def add_error(self, error: ValidationError):
        self._errors.append(error)

    @property 
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, value: list):
        self._errors = value

    @property
    def path(self):
        return self._path_stack
    
    @path.setter
    def path(self, value: list):
        self._path_stack = value

    @property
    def depth(self):
        return len(self._path_stack)

    @classmethod
    def _join_contexts(cls, other: 'ValidationContext') -> 'ValidationContext':
        new_ctx = ValidationContext()
        new_ctx.errors = other.errors
        new_ctx.path = other.path
        
        return new_ctx
    
    @classmethod
    def init_context(cls, context: Self | None):
        if not context:
            return ValidationContext()
                
        return cls._join_contexts(context)