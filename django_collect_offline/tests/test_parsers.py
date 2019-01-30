from django.core import serializers
from django.test import TestCase, tag

from ..transaction import deserialize
from ..parsers import datetime_to_date_parser
from .models import TestModelDates


class TestParsers(TestCase):
    def test_date_parser(self):
        datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        obj = TestModelDates.objects.create()
        json_text = serializers.serialize("json", [obj])
        bad_date = obj.f3.strftime(datetime_format)
        json_text = json_text.replace("null", f'"{bad_date}"')
        json_text = datetime_to_date_parser(
            json_text, model="django_collect_offline.testmodeldates", field="f2"
        )
        json_data = deserialize(json_text)
        for obj in json_data:
            self.assertEqual(obj.object.f3.date(), obj.object.f2)

    def test_date_parser_with_null(self):
        obj = TestModelDates.objects.create()
        json_text = serializers.serialize("json", [obj])
        json_text = datetime_to_date_parser(json_text, field="f2")
        json_data = deserialize(json_text)
        for obj in json_data:
            self.assertIsNone(obj.object.f2)

    def test_date_parser_with_none(self):
        try:
            datetime_to_date_parser(
                None, model="django_collect_offline.testmodeldates", field="f2"
            )
        except TypeError:
            self.fail("the JSON object must be str, bytes or bytearry, not NoneType")

    def test_date_parser_with_bad_fieldname(self):
        obj = TestModelDates.objects.create()
        json_text = serializers.serialize("json", [obj])
        self.assertEqual(json_text, datetime_to_date_parser(json_text, field="blah"))

    def test_date_parser_with_no_fieldname(self):
        obj = TestModelDates.objects.create()
        json_text = serializers.serialize("json", [obj])
        self.assertEqual(json_text, datetime_to_date_parser(json_text))
