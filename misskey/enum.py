from enum import Enum, unique


@unique
class NoteVisibility(Enum):
    PUBLIC = 'public'
    HOME = 'home'
    FOLLOWERS = 'followers'
    SPECIFIED = 'specified'


@unique
class NotificationsType(Enum):
    FOLLOW = 'follow'
    MENTIONS = 'mention'
    REPLY = 'reply'
    RENOTE = 'renote'
    QUOTE = 'quote'
    REACTION = 'reaction'
    POLL_VOTE = 'pollVote'
    RECEIVE_FOLLOW_REQUEST = 'receiveFollowRequest'
    FOLLOW_REQUEST_ACCEPTED = 'followRequestAccepted'
    GROUP_INVITED = 'groupInvited'
    APP = 'app'
