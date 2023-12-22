import datetime


class MisskeyID(object):
    id: str

    def __str__(self) -> str:
        return self.id

    @classmethod
    def generate(cls, *args, **kwargs):
        raise NotImplementedError()

    def to_date(self) -> datetime.datetime:
        raise NotImplementedError()
