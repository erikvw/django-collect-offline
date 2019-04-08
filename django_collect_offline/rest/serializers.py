from rest_framework import serializers


class ModelSerializerMixin:

    model_class = None

    user_created = serializers.CharField(max_length=50, allow_blank=True)

    user_modified = serializers.CharField(max_length=50, allow_blank=True)

    hostname_created = serializers.CharField(max_length=50, allow_blank=True)

    hostname_modified = serializers.CharField(max_length=50, allow_blank=True)

    revision = serializers.CharField(max_length=75)

    def create(self, validated_data):
        return self.model_class.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for fieldname in [fld.name for fld in self.model_class._meta.fields]:
            setattr(
                instance,
                fieldname,
                validated_data.get(fieldname, getattr(instance, fieldname)),
            )
        instance.save()
        return instance
