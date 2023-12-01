from marshmallow import Schema, fields

from misskey.enum import (
    UsersSortEnum,
    UsersStateEnum,
    UsersOriginEnum,
)


__all__ = (
    "UsersArgumentsSchema",
)


class UsersArgumentsSchema(Schema):
    limit = fields.Integer(default=10)
    offset = fields.Integer(default=0)
    sort = fields.Enum(UsersSortEnum, by_value=True)
    state = fields.Enum(
        UsersStateEnum, by_value=True, default=UsersStateEnum.ALL)
    origin = fields.Enum(
        UsersOriginEnum, by_value=True, default=UsersOriginEnum.LOCAL)
    hostname = fields.String(allow_none=True)
