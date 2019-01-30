import json

from django.core.serializers.json import DjangoJSONEncoder


def datetime_to_date_parser(json_text, model=None, field=None):

    if model and field:
        try:
            json_data = json.loads(json_text)
        except TypeError:
            pass
        else:
            fields = json_data[0]["fields"]
            if model == json_data[0]["model"] and field in fields:
                json_data[0]["fields"][field] = fields[field][:10]
                json_text = json.dumps(json_data, cls=DjangoJSONEncoder)
    return json_text
