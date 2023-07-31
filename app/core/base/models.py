from tortoise import models, fields


class BaseDBModel(models.Model):
    class Meta:
        abstract = True
    id = fields.BigIntField(pk=True, index=True)

    async def to_dict(self):
        d = {}
        for field in self._meta.db_fields:
            d[field] = getattr(self, field)
        for field in self._meta.backward_fk_fields:
            d[field] = await getattr(self, field).all().values()
        return d


class BaseCreatedAtModel:
    created_at = fields.DatetimeField(auto_now_add=True)


class BaseCreatedUpdatedAtModel:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class LocationModel:
    latitude = fields.DecimalField(max_digits=9, decimal_places=6)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6)
