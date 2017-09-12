import json

from dateutil.parser import parse
from django.apps import apps as django_apps


def date_parse_value(json_text, override_sync_data_values=None):
    json_data = json.loads(json_text)
    override_sync_data_values = django_apps.get_app_config(
        'edc_sync').override_sync_data_values or override_sync_data_values
    for item in override_sync_data_values or []:
        for (key, fields) in item.items():
            tmp_data = json_data[0]
            if tmp_data.get('model') == key:
                fields_data = tmp_data.get('fields')
                for field in fields:
                    try:
                        old_value = fields_data.get(field)
                        new_value = parse(old_value).strftime('%Y-%m-%d')
                        old_value_format = f"\"{field}\": \"{old_value}\""
                        new_value_format = f"\"{field}\": \"{new_value}\""
                        json_text = json_text.replace(
                            old_value_format, new_value_format)
                    except (ValueError, TypeError):
                        pass
    return json_text
