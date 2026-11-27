from notification import settings


class DbRoutingSerializerMixin:
    """Routes create/update ORM operations to the configured notification database alias."""

    default_using = None

    def _get_using(self, validated_data):
        default_db = self.default_using or settings.get_db()
        return validated_data.pop('using', default_db)

    def create(self, validated_data):
        using_db = self._get_using(validated_data)
        return self.Meta.model.objects.using(using_db).create(**validated_data)

    def update(self, instance, validated_data):
        using_db = self._get_using(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(using=using_db)
        return instance
