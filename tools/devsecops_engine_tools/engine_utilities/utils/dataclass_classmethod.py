import dataclasses
import typing
import datetime
import enum
from inspect import isclass
from typing import get_type_hints
from .alias import Alias
from .name_conversion import camel_case_to_snake_case, snake_case_to_camel_case
from .datetime_parsing import iso_from_datetime, parse_iso_datetime


class FromDictMixin:
    _exclude_none: bool = False

    @staticmethod
    def _resolve_union_type(union_type):
        """Extract the non-None type from Optional/Union types (e.g., Optional[X] -> X)"""
        if hasattr(union_type, '__origin__') and union_type.__origin__ is typing.Union:
            args = union_type.__args__
            # Filter out NoneType to get the actual type
            non_none_types = [arg for arg in args if arg is not type(None)]
            if non_none_types:
                return non_none_types[0]
        return union_type

    @staticmethod
    def attribute_to_dict(attribute):
        if hasattr(attribute, "to_dict") and callable(attribute.to_dict):
            return getattr(attribute, "to_dict")()
        return attribute

    @staticmethod
    def _resolve_key(field_name, hints):
        hint = hints.get(field_name)
        if hasattr(hint, "__metadata__"):
            for meta in hint.__metadata__:
                if isinstance(meta, Alias):
                    return meta.name
        return snake_case_to_camel_case(field_name)

    def to_dict(self):
        if self == {}:
            return self
        hints = get_type_hints(self.__class__, include_extras=True)
        available_fields = {field.name: field for field in dataclasses.fields(self)}
        transformed_data = {}
        for field_name, field_type in available_fields.items():
            if field_name.startswith("_"):
                continue
            attribute = getattr(self, field_name)
            if self._exclude_none and attribute is None:
                continue
            key = self._resolve_key(field_name, hints)
            if isinstance(attribute, list):
                transformed_data[key] = []
                for element in attribute:
                    transformed_data[key].append(FromDictMixin.attribute_to_dict(element))
            elif isinstance(attribute, dict):
                transformed_data[key] = {}
                for k, element in attribute.items():
                    transformed_data[key][k] = FromDictMixin.attribute_to_dict(element)
            elif isinstance(attribute, enum.Enum):
                transformed_data[key] = attribute.value
            elif isinstance(attribute, datetime.datetime):
                transformed_data[key] = iso_from_datetime(attribute)
            else:
                transformed_data[key] = FromDictMixin.attribute_to_dict(attribute)
        return transformed_data

    @classmethod
    def from_dict(cls, data):
        built_in_types = (int, str, bool, float)
        available_fields = {field.name: field for field in dataclasses.fields(cls)}
        transformed_data = {}
        for key, value in data.items():
            internal_key = camel_case_to_snake_case(key)
            if internal_key in available_fields.keys() and value is not None:
                matching_internal_field = available_fields[internal_key]
                # Resolve Union/Optional types to get the actual type
                field_type = cls._resolve_union_type(matching_internal_field.type)
                
                if field_type in built_in_types:
                    internal_value = value
                elif field_type == datetime.datetime and value:
                    internal_value = parse_iso_datetime(value)
                elif isclass(field_type) and issubclass(field_type, enum.Enum):
                    internal_value = field_type(value)
                elif hasattr(field_type, "from_dict") and callable(field_type.from_dict):
                    internal_value = field_type.from_dict(value)
                elif (
                    isinstance(field_type, typing._GenericAlias)
                    and field_type.__origin__ == list
                ):
                    value_class = field_type.__args__[0]
                    internal_value = []
                    if hasattr(value_class, "from_dict") and callable(value_class.from_dict):
                        internal_value = [value_class.from_dict(v) for v in value]
                    else:
                        internal_value = [v for v in value]
                elif (
                    isinstance(field_type, typing._GenericAlias)
                    and field_type.__origin__ == dict
                ):
                    value_class = field_type.__args__[1]
                    internal_value = {}
                    if hasattr(value_class, "from_dict") and callable(value_class.from_dict):
                        internal_value = {k: value_class.from_dict(v) for k, v in value.items()}
                    else:
                        internal_value = value
                else:
                    internal_value = None
                if internal_value is not None:
                    transformed_data[internal_key] = internal_value
        return cls(**transformed_data)
