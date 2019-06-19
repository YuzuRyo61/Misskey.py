# API TODO

## app

- [x] app/create
- [ ] app/show
- [x] app/session/generate
- [x] app/session/userkey

## blocking

- [x] blocking/create
- [x] blocking/delete
- [x] blocking/list

## users

- [x] username/available
- [x] users
- [x] users/followers
- [x] users/following
- [ ] users/get-frequently-replied-users
- [ ] users/notes
- [ ] users/recommendation
- [ ] users/relation
- [ ] users/report-abuse
- [ ] users/search
- [x] users/show
- [ ] pinned-users (Misskey: >=1.12.0)

## account

- [x] i
- [x] i/favorites
- [x] i/notifications
- [x] i/pin
- [x] i/read-all-messaging-messages
- [x] i/read-all-unread-notes
- [x] i/unpin
- [x] i/update
- [ ] my/apps
- [x] notifications/mark-all-as-read

## drive

- [x] drive
- [x] drive/files
- [x] drive/files/attached-notes
- [x] drive/files/check-existence
- [x] drive/files/create
- [x] drive/files/delete
- [x] drive/files/find
- [x] drive/files/show
- [x] drive/files/update
- [x] drive/files/upload-from-url
- [x] drive/folders
- [x] drive/folders/create
- [x] drive/folders/delete
- [x] drive/folders/find
- [x] drive/folders/show
- [x] drive/folders/update
- [x] drive/stream

## hashtags

- [ ] hashtags/list
- [ ] hashtags/search
- [ ] hashtags/trend
- [ ] hashtags/users

## notes

- [x] notes
- [ ] notes/children
- [ ] notes/conversation
- [x] notes/create
- [x] notes/delete
- [ ] notes/featured
- [x] notes/global-timeline
- [x] notes/hybrid-timeline
- [x] notes/local-timeline
- [ ] notes/mentions
- [ ] notes/polls/recommendation
- [x] notes/polls/vote
- [x] notes/reactions
- [x] notes/reactions/create
- [x] notes/reactions/delete
- [x] notes/renotes
- [ ] notes/replies
- [ ] notes/search-by-tag
- [ ] notes/search
- [x] notes/show
- [ ] notes/state
- [ ] notes/timeline
- [x] notes/user-list-timeline
- [ ] notes/watching/create
- [ ] notes/watching/delete
- [x] users/notes

## following

- [x] following/create
- [x] following/delete
- [ ] following/requests/accept
- [ ] following/requests/cancel
- [ ] following/requests/list
- [ ] following/requests/reject

## favorites

- [x] notes/favorites/create
- [x] notes/favorites/delete

## messaging

- [x] messaging/history
- [x] messaging/messages
- [x] messaging/messages/create
- [x] messaging/messages/delete
- [x] messaging/messages/read

## meta

- [x] meta
- [x] stats

## mute

- [x] mute/create
- [x] mute/delete
- [x] mute/list

## lists

- [x] users/lists/create
- [x] users/lists/delete
- [x] users/lists/list
- [x] users/lists/pull
- [x] users/lists/push
- [x] users/lists/show
- [x] users/lists/update

## pages (Misskey: >=11.5.0)

- [ ] i/pages
- [ ] pages/create
- [ ] pages/delete
- [ ] pages/show
- [ ] pages/update

## groups (Misskey: >= 11.16.0)

- [ ] users/groups/create
- [ ] users/groups/delete
- [ ] users/groups/joined
- [ ] users/groups/owned
- [ ] users/groups/pull
- [ ] users/groups/push
- [ ] users/groups/show
- [ ] users/groups/invitations/accept (Misskey: >= 11.17.0)
- [ ] users/groups/invitations/reject (Misskey: >= 11.17.0)
- [ ] users/groups/invite (Misskey: >= 11.17.0)

Info: **I will not implement chart and game API**
