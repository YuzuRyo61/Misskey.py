from enum import Enum, unique


@unique
class NoteVisibility(Enum):
    PUBLIC = 'public'
    HOME = 'home'
    FOLLOWERS = 'followers'
    SPECIFIED = 'specified'
