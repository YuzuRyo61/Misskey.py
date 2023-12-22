from marshmallow import Schema, fields

__all__ = (
    "NotesLocalTimelineArgumentsSchema",
)


class NotesLocalTimelineArgumentsSchema(Schema):
    with_files = fields.Boolean(default=False, data_key="withFiles")
    with_renotes = fields.Boolean(default=False, data_key="withRenotes")
    with_replies = fields.Boolean(default=False, data_key="withReplies")
    exclude_nsfw = fields.Boolean(default=False, data_key="excludeNsfw")
    limit = fields.Integer(default=10)
    since_id = fields.String(data_key="sinceId")
    until_id = fields.String(data_key="untilId")
    since_date = fields.DateTime("timestamp_ms", data_key="sinceDate")
    until_date = fields.DateTime("timestamp_ms", data_key="untilDate")
