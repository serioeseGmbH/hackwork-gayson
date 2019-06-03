from unittest import TestCase
from datetime import datetime, time, date, timedelta
from uuid import UUID

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
