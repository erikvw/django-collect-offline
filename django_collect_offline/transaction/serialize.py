from django.core import serializers


def serialize(objects=None):
    """A simple wrapper of Django's serializer with defaults
    for JSON and natural keys.

    Note: use_natural_primary_keys is False as once
    a pk is set, it should not be changed throughout the
    distributed data.
    """

    return serializers.serialize(
        "json",
        objects,
        ensure_ascii=True,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=False,
    )
