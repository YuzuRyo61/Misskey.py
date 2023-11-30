from marshmallow import Schema, fields

__all__ = (
    "AnnouncementsArgumentsSchema",
)


class AnnouncementsArgumentsSchema(Schema):
    limit = fields.Integer(default=10)
    with_unreads = fields.Boolean(default=False, data_key="withUnreads")
    since_id = fields.String(data_key="sinceId")
    until_id = fields.String(data_key="untilId")
