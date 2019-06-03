import collections
from abc import ABC, ABCMeta, abstractmethod

import re
from datetime import datetime, date, time, timedelta
from typing import Any, Union, Dict, List
from uuid import UUID

import rapidjson


class Convert(ABCMeta):
    __key_to_converter__ = {}
    __type_to_converter__ = {}
    __key_to_type__ = {}
    __type_to_key__ = {}

    def __new__(mcs, name, *args, **kwargs):
        cls = super().__new__(mcs, name, *args, **kwargs)
        if cls.__base__ == object or cls.__base__ == ABC:
            # so that we can define our base class in peace
            return cls

        key = getattr(cls, 'key', None)
        python_type = getattr(cls, 'python_type', None)
        if not issubclass(type(python_type), type):
            raise ValueError(
                f"{python_type} is not a valid python type."
            )
        if not callable(getattr(cls, 'value_to_json', None)) or\
                not callable(getattr(cls, 'json_to_value', None)):
            raise ValueError(
                "A Converter class must implement value_to_json and "
                "json_to_value."
            )

        mcs.__key_to_converter__[key] = cls
        mcs.__type_to_converter__[python_type] = cls
        mcs.__key_to_type__[key] = python_type
        mcs.__type_to_key__[python_type] = key

    @classmethod
    def value_to_json(mcs, value):
        converter_cls = mcs.__type_to_converter__.get(type(value), None)
        if converter_cls is None:
            raise ValueError(f"Can not convert object of type {type(value)}!")
        return converter_cls.value_to_json(value)

    @classmethod
    def json_to_value(mcs, json: collections.Mapping):
        key = json.get('__type__', None)
        value = json.get('value', None)
        if key is None:
            raise ValueError(f"Can not convert with missing type key!")
        if value is None:
            raise ValueError(f"Can not convert with missing value!")
        converter_cls = mcs.__key_to_converter__.get(key, None)
        if converter_cls is None:
            raise ValueError(f"Can not convert object of type key {key}!")
        return converter_cls.json_to_value(value)

    @classmethod
    def dumps_default(mcs, value: Any):
        type_ = type(value)
        if type_ in mcs.__type_to_converter__:
            return {
                "__type__": mcs.__type_to_key__[type_],
                "value": mcs.value_to_json(value)
            }
        else:
            return value

    @classmethod
    def loads_object_hook(mcs, json: Union[Dict, List, str, int, float, bool]):
        if isinstance(json, collections.Mapping) and '__type__' in json:
            return mcs.json_to_value(json)
        else:
            return json

    @classmethod
    def loads(mcs, json_string: str):
        return rapidjson.loads(json_string, object_hook=mcs.loads_object_hook)

    @classmethod
    def dumps(mcs, json_dict: Dict):
        return rapidjson.dumps(json_dict, default=mcs.dumps_default)


class Converter(ABC, metaclass=Convert):
    @classmethod
    @abstractmethod
    def value_to_json(cls, value: Any):
        pass

    @classmethod
    @abstractmethod
    def json_to_value(cls, jsonvalue: str):
        pass


class TimeConverter(Converter):
    python_type = time
    key = 'time'

    time_format = re.compile(r'\d\d:\d\d:\d\d[+|-]\d\d:\d\d')

    @classmethod
    def json_to_value(cls, jsonvalue):
        if not cls.time_format.match(jsonvalue):
            raise ValueError('Value does not match hh:mm:ss(+|-)hh:mm format!')
        else:
            t = time.fromisoformat(jsonvalue)
        if not t.tzinfo:
            raise ValueError('Timezone is missing!')
        else:
            return t

    @classmethod
    def value_to_json(cls, value: time):
        if type(value) is not time:
            raise TypeError(f'{value} must be a datetime.time.')
        elif not value.tzinfo:
            raise ValueError(
                f'{value} must be aware. I.e. it must contain tzinfo.')
        else:
            return str(value)


class DateConverter(Converter):
    """
    A date in YYYY-MM-DD format
    """
    python_type = date
    key = "date"

    @classmethod
    def value_to_json(cls, value: date):
        if type(value) is not date:
            raise TypeError(f'{value} must be a datetime.date.')
        else:
            return str(value)

    @classmethod
    def json_to_value(cls, jsonvalue: str):
        return datetime.strptime(jsonvalue, '%Y-%m-%d').date()


class DatetimeConverter(Converter):
    """
        A datetime in YYYY-MM-DDThh:mm:ss(+|-)hh:mm format. The datetime must be
        aware. I.e. it must contain timezone information.
        """
    python_type = datetime
    key = "datetime"

    @classmethod
    def value_to_json(cls, value: datetime):
        if type(value) is not datetime:
            raise TypeError(f'{value} must be a datetime.datetime.')
        elif not value.tzinfo:
            raise ValueError(
                f'{value} must be aware. I.e. it must contain tzinfo.')
        else:
            return str(value).replace(' ', 'T')

    @classmethod
    def json_to_value(cls, jsonvalue: str):
        dt = datetime.fromisoformat(jsonvalue)
        if not dt.tzinfo:
            raise ValueError('Timezone is missing!')
        else:
            return dt


class TimedeltaConverter(Converter):
    python_type = timedelta
    key = "timedelta"

    @classmethod
    def value_to_json(cls, value: timedelta):
        if type(value) is not timedelta:
            raise TypeError(f'{value} must be a datetime.timedelta.')
        else:
            return str(value.total_seconds())

    @classmethod
    def json_to_value(cls, jsonvalue: str):
        return timedelta(seconds=float(jsonvalue))


class UUIDConverter(Converter):
    python_type = UUID
    key = 'uuid'

    uuid_format = re.compile(
        '[0-9a-fA-F]{8}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-[0-9a-fA-F]{4}\\-['
        '0-9a-fA-F]{12}'
    )  # Regex to check for UUID RFC 4122 string representation format.

    @classmethod
    def value_to_json(cls, value: UUID):
        if type(value) is not UUID:
            raise TypeError(f'{value} must be a uuid.UUID.')
        else:
            return str(value)

    @classmethod
    def json_to_value(cls, jsonvalue: str):
        if not cls.uuid_format.match(jsonvalue):
            raise ValueError(
                'Value does not match UUID RFC 4122 string representation '
                'format!'
            )
        else:
            return UUID(jsonvalue)
