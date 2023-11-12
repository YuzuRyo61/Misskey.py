from marshmallow import Schema, fields

__all__ = (
    "MisskeyUser",
)


class MisskeyUser(Schema):
    id = fields.String(required=True)
    created_at = fields.DateTime(data_key="createdAt", required=True)
    username = fields.String(required=True)
    host = fields.String()

    class Meta:
        strict = True
