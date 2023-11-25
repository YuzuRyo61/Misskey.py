from marshmallow import Schema, fields

__all__ = (
    "MisskeyNotesDeleteSchema",
)


class MisskeyNotesDeleteSchema(Schema):
    note_id = fields.String(required=True, data_key="noteId")
