from unittest import TestCase
from datetime import datetime, time, date, timedelta
from uuid import UUID

import json
import pytz

from .convert import Convert


class ConvertTest(TestCase):
    tz = pytz.timezone('Europe/Berlin')

    def test_datetime_bidirectional_conversion_is_identity(self):
        now = self.tz.localize(datetime.now())
        now_as_json = Convert.value_to_json(now)
        now_from_json = Convert.json_to_value({'__type__': 'datetime',
                                               'value': now_as_json})
        self.assertEqual(now, now_from_json)

    def test_expected_type_keys_are_registered(self):
        for key in ['datetime', 'time', 'date', 'timedelta', 'uuid']:
            self.assertIn(key, Convert.__key_to_converter__)

    def test_expected_types_are_registered(self):
        for type_ in [datetime, time, date, timedelta, UUID]:
            self.assertIn(type_, Convert.__type_to_converter__)

    def test_loads_only_changes_nonconvertible_fields(self):
        data = {
            'xyz': 1,
            'brot': "6000",
            'uwe': True,
            'somedate': {'__type__': 'date', 'value': '1960-01-01'}
        }
        data = Convert.loads(json.dumps(data))
        self.assertEqual(data['xyz'], 1)
        self.assertEqual(data['brot'], "6000")
        self.assertEqual(data['uwe'], True)
        self.assertEqual(data['somedate'], date(1960, 1, 1))

    def test_dumps_only_changes_nonconvertible_fields(self):
        data = {
            'xyz': 1,
            'brot': "6000",
            'uwe': True,
            'somedate': {'__type__': 'date', 'value': '1960-01-01'}
        }
        data = json.loads(Convert.dumps(data))

        self.assertEqual(data['xyz'], 1)
        self.assertEqual(data['brot'], "6000")
        self.assertEqual(data['uwe'], True)
        self.assertEqual(data['somedate'], {'__type__': 'date', 'value': '1960-01-01'})

    def test_dumps(self):
        data = {
            'xyz': 1,
            'somedate': date(1960, 1, 1)
        }
        json_string = Convert.dumps(data)
        self.assertIsInstance(json_string, str)
        self.assertEqual(
            json_string,
            '{"xyz":1,"somedate":{"__type__":"date","value":"1960-01-01"}}'
        )

    def test_loads(self):
        json_string = '{"xyz":1,"somedate":{"__type__":"date","value":"1960-01-01"}}'
        data = Convert.loads(json_string)
        self.assertIsInstance(data, dict)
        self.assertEqual(
            data,
            {
                'xyz': 1,
                'somedate': date(1960, 1, 1)
            }
        )

    def test_loads_dumps_compositions_are_identity(self):
        json_string = '{"xyz":1,"somedate":{"__type__":"date","value":"1960-01-01"}}'
        data = {
            'xyz': 1,
            'somedate': date(1960, 1, 1)
        }

        self.assertEqual(data, Convert.loads(Convert.dumps(data)))
        self.assertEqual(json_string, Convert.dumps(Convert.loads(json_string)))
