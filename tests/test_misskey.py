import datetime
import io
import uuid
from urllib.parse import urlparse

import pytest
import requests

from misskey import (
    Misskey,
    NotificationsType
)
from misskey.exceptions import (
    MisskeyAuthorizeFailedException,
    MisskeyAPIException,
)
from .conftest import TEST_HOST


@pytest.mark.parametrize('host', [
    'http://unknown-host',
    'unknown-host',
])
def test_should_connect_error_in_init(host: str):
    with pytest.raises(requests.exceptions.ConnectionError):
        Misskey(host)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, '')
])
def test_should_token_error_in_init(host: str, token: str):
    with pytest.raises(MisskeyAuthorizeFailedException):
        Misskey(host, i=TEST_HOST)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, ''),
])
def test_should_token_error_in_setter(host: str, token: str):
    with pytest.raises(MisskeyAuthorizeFailedException):
        mk = Misskey(host)
        mk.token = token


def test_address_should_be_same(mk_cli_anon: Misskey):
    host_url = urlparse(TEST_HOST)
    assert mk_cli_anon.address == host_url.netloc


def test_token_should_be_valid(
    mk_cli_user: Misskey,
    mk_user_token: str
):
    assert mk_cli_user.token == mk_user_token


def test_token_should_be_settable_and_deletable(mk_user_token: str):
    mk = Misskey(TEST_HOST)
    mk.token = mk_user_token
    assert type(mk.token) == str
    del mk.token
    assert mk.token is None


def test_should_success_i(mk_cli_user: Misskey):
    res = mk_cli_user.i()
    assert type(res) == dict


def test_should_fail_i(mk_cli_anon: Misskey):
    with pytest.raises(MisskeyAPIException) as e:
        mk_cli_anon.i()

    assert type(e.value.code) == str
    assert type(e.value.message) == str
    assert type(e.value.id) == uuid.UUID or type(e.value.id) == str


def test_meta(mk_cli_anon: Misskey):
    res = mk_cli_anon.meta()
    assert type(res) == dict


def test_stats(mk_cli_anon: Misskey):
    res = mk_cli_anon.stats()
    assert type(res) == dict


def test_emojis(mk_cli_anon: Misskey):
    res = mk_cli_anon.emojis()
    assert type(res) == dict


def test_endpoint(mk_cli_anon: Misskey):
    res = mk_cli_anon.endpoint('endpoint')
    assert type(res) == dict


def test_endpoints(mk_cli_anon: Misskey):
    res = mk_cli_anon.endpoints()
    assert type(res) == list


def test_fetch_rss(mk_cli_anon: Misskey):
    res = mk_cli_anon.fetch_rss('http://feeds.afpbb.com/rss/afpbb/afpbbnews')
    assert type(res) == dict


def test_get_online_users_count(mk_cli_anon: Misskey):
    res = mk_cli_anon.get_online_users_count()
    assert type(res) == dict


def test_ping(mk_cli_anon: Misskey):
    res = mk_cli_anon.ping()
    assert type(res) == dict


def test_server_info(mk_cli_anon: Misskey):
    res = mk_cli_anon.server_info()
    assert type(res) == dict


def test_i_favorites(mk_cli_admin: Misskey):
    res = mk_cli_admin.i_favorites()
    assert type(res) == list


def test_should_be_viewable_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str
):
    res = mk_cli_admin.notes_show(mk_admin_new_note)
    assert type(res) == dict


def test_note_poll_expires_at(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    res = mk_cli_admin.notes_create(
        text='poll test (expires_at)',
        poll_choices=[
            'test 1',
            'test 2',
        ],
        poll_expires_at=(
            datetime.datetime.now() +
            datetime.timedelta(minutes=1)
        ),
    )
    assert type(res) == dict

    vote_res = mk_cli_user.notes_polls_vote(
        res['createdNote']['id'],
        0,
    )
    assert type(vote_res) == bool
    assert vote_res

    is_deleted = mk_cli_admin.notes_delete(res['createdNote']['id'])
    assert type(is_deleted) == bool
    assert is_deleted


def test_note_poll_expired_after(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    res = mk_cli_admin.notes_create(
        text='poll test (expired_after)',
        poll_choices=[
            'test 1',
            'test 2',
        ],
        poll_expired_after=datetime.timedelta(minutes=1),
    )
    assert type(res) == dict

    vote_res = mk_cli_user.notes_polls_vote(
        res['createdNote']['id'],
        0,
    )
    assert type(vote_res) == bool
    assert vote_res

    is_deleted = mk_cli_admin.notes_delete(res['createdNote']['id'])
    assert type(is_deleted) == bool
    assert is_deleted


def test_should_be_error_in_create_note_visibility(
    mk_cli_admin: Misskey,
):
    with pytest.raises(ValueError):
        mk_cli_admin.notes_create(visibility='not valid visibility')


def test_i_notifications(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.i_notifications(
        include_types={
            NotificationsType.REACTION
        },
    )
    assert type(res) == list


def test_notifications_mark_all_as_read(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.notifications_mark_all_as_read()
    assert type(res) == bool
    assert res


def test_notifications(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.notifications_create(
        body='test-notification',
    )
    assert type(res_create) == bool
    assert res_create

    res_notifications = mk_cli_admin.i_notifications()
    assert type(res_notifications) == list
    assert len(res_notifications) > 0

    res_read = mk_cli_admin.notifications_read(
        res_notifications[0]['id'],
    )
    assert type(res_read) == bool
    assert res_read


def test_should_be_error_in_i_notifications(
    mk_cli_admin: Misskey,
):
    with pytest.raises(ValueError):
        mk_cli_admin.i_notifications(
            include_types=[
                'unknown_type'
            ]
        )

    with pytest.raises(ValueError):
        mk_cli_admin.i_notifications(
            exclude_types=[
                'unknown_type'
            ]
        )


def test_should_can_be_pin_and_unpin_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res_pin = mk_cli_admin.i_pin(mk_admin_new_note)
    assert type(res_pin) == dict
    res_unpin = mk_cli_admin.i_unpin(mk_admin_new_note)
    assert type(res_unpin) == dict


def test_should_ok_show_replies(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_renotes(mk_admin_new_note)
    assert type(res) == list


def test_should_ok_show_reactions(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_reactions(
        mk_admin_new_note,
        reaction_type='✅',
    )
    assert type(res) == list


def test_should_can_be_reaction_to_notes(
    mk_cli_user: Misskey,
    mk_admin_new_note: str,
):
    res_reaction = mk_cli_user.notes_reactions_create(
        mk_admin_new_note,
        '✅',
    )
    assert type(res_reaction) == bool
    assert res_reaction
    res_del_reaction = mk_cli_user.notes_reactions_delete(
        mk_admin_new_note,
    )
    assert type(res_del_reaction) == bool
    assert res_del_reaction


def test_notes_timeline(
    mk_cli_admin: Misskey,
):
    timeline = mk_cli_admin.notes_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline) == list


def test_notes_local_timeline(
    mk_cli_admin: Misskey,
):
    timeline_local = mk_cli_admin.notes_local_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline_local) == list


def test_notes_hybrid_timeline(
    mk_cli_admin: Misskey,
):
    timeline_hybrid = mk_cli_admin.notes_hybrid_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline_hybrid) == list


def test_notes_global_timeline(
    mk_cli_admin: Misskey,
):
    timeline_global = mk_cli_admin.notes_global_timeline(
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(timeline_global) == list


def test_notes_replies(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_replies(mk_admin_new_note)
    assert type(res) == list


def test_renote_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_create(
        renote_id=mk_admin_new_note,
    )
    assert type(res) == dict

    res_unrenote = mk_cli_admin.notes_unrenote(
        mk_admin_new_note,
    )
    assert type(res_unrenote) == bool
    assert res_unrenote


def test_favorite_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res_favorite = mk_cli_admin.notes_favorites_create(
        mk_admin_new_note,
    )
    assert type(res_favorite) == bool
    assert res_favorite

    res_unfav = mk_cli_admin.notes_favorites_delete(
        mk_admin_new_note,
    )
    assert type(res_unfav) == bool
    assert res_unfav


def test_notes_conversation(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_conversation(
        mk_admin_new_note,
    )
    assert type(res) == list


def test_notes_children(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_children(
        mk_admin_new_note,
    )
    assert type(res) == list


def test_announcements(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.announcements()
    assert type(res) == list


def test_notes_state(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_state(
        mk_admin_new_note,
    )
    assert type(res) == dict


def test_notes(
    mk_cli_admin: Misskey,
):
    res_notes = mk_cli_admin.notes()
    assert type(res_notes) == list

    res_featured = mk_cli_admin.notes_featured()
    assert type(res_featured) == list

    res_mentions = mk_cli_admin.notes_mentions(
        visibility='public',
    )
    assert type(res_mentions) == list


def test_notes_clips(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res = mk_cli_admin.notes_clips(mk_admin_new_note)
    assert type(res) == list


def test_notes_polls_recommendation(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.notes_polls_recommendation()
    assert type(res) == list


def test_notes_search(
    mk_cli_admin: Misskey,
):
    res_search = mk_cli_admin.notes_search('test')
    assert type(res_search) == list

    res_search_by_tag = mk_cli_admin.notes_search_by_tag(
        [['fediverse'], ['misskey', 'ai']]
    )
    assert type(res_search_by_tag) == list


def test_notes_thread_muting(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res_create = mk_cli_admin.notes_thread_muting_create(mk_admin_new_note)
    assert type(res_create) == bool
    assert res_create

    res_delete = mk_cli_admin.notes_thread_muting_delete(mk_admin_new_note)
    assert type(res_delete) == bool
    assert res_delete


def test_notes_user_list_timeline(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.users_lists_create('test-list')
    assert type(res_create) == dict

    res_user_list_timeline = mk_cli_admin.notes_user_list_timeline(
        list_id=res_create['id'],
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now() +
            datetime.timedelta(hours=3)
        )
    )
    assert type(res_user_list_timeline) == list


def test_i_update(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.i_update(
        name='Unit test user admin',
        birthday=datetime.date.today(),
        lang='ja-JP',
        fields={'name1': 'value1', 'name2': 'value2'},
        ff_visibility='private',
        muting_notification_types=[
            'app',
        ],
        email_notification_types=(
            'follow',
            'mention',
        ),
    )
    assert type(res) == dict


def test_i_export(
    mk_cli_admin: Misskey,
):
    res_blocking = mk_cli_admin.i_export_blocking()
    assert type(res_blocking) == bool
    assert res_blocking

    res_favorites = mk_cli_admin.i_export_favorites()
    assert type(res_favorites) == bool
    assert res_favorites

    res_following = mk_cli_admin.i_export_following()
    assert type(res_following) == bool
    assert res_following

    res_mute = mk_cli_admin.i_export_mute()
    assert type(res_mute) == bool
    assert res_mute

    res_notes = mk_cli_admin.i_export_notes()
    assert type(res_notes) == bool
    assert res_notes

    res_user_lists = mk_cli_admin.i_export_user_lists()
    assert type(res_user_lists) == bool
    assert res_user_lists


def test_i_gallery(
    mk_cli_admin: Misskey,
):
    res_gallery_likes = mk_cli_admin.i_gallery_likes()
    assert type(res_gallery_likes) == list

    res_gallery_posts = mk_cli_admin.i_gallery_posts()
    assert type(res_gallery_posts) == list


def test_i_get_word_muted_notes_count(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.i_get_word_muted_notes_count()
    assert type(res) == dict


def test_i_import(
    mk_cli_admin: Misskey,
):
    res_files_create = mk_cli_admin.drive_files_create(
        io.StringIO('test-import'),
        name='empty.csv',
    )
    assert type(res_files_create) == dict

    res_import_blocking = mk_cli_admin.i_import_blocking(
        res_files_create['id']
    )
    assert type(res_import_blocking) == bool
    assert res_import_blocking

    res_import_following = mk_cli_admin.i_import_following(
        res_files_create['id']
    )
    assert type(res_import_following) == bool
    assert res_import_following

    res_import_muting = mk_cli_admin.i_import_muting(
        res_files_create['id']
    )
    assert type(res_import_muting) == bool
    assert res_import_muting

    res_import_user_lists = mk_cli_admin.i_import_user_lists(
        res_files_create['id']
    )
    assert type(res_import_user_lists) == bool
    assert res_import_user_lists


def test_i_page(
    mk_cli_admin: Misskey,
):
    res_page_likes = mk_cli_admin.i_page_likes()
    assert type(res_page_likes) == list

    res_pages = mk_cli_admin.i_pages()
    assert type(res_pages) == list


def test_i_read(
    mk_cli_admin: Misskey,
):
    res_all_unread_notes = mk_cli_admin.i_read_all_unread_notes()
    assert type(res_all_unread_notes) == bool
    assert res_all_unread_notes

    res_create = requests.post(
        f"{TEST_HOST}/api/admin/announcements/create",
        json={
            'i': mk_cli_admin.token,
            'title': 'test-announcement',
            'text': 'test-announcement',
            'imageUrl': None,
        }
    ).json()
    res_announcement = mk_cli_admin.i_read_announcement(
        res_create['id']
    )
    assert type(res_announcement) == bool
    assert res_announcement


def test_i_webhooks(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.i_webhooks_create(
        name='test-webhook',
        url='test-webhook',
        secret='test-webhook',
        on=['mention'],
    )
    assert type(res_create) == dict

    res_list = mk_cli_admin.i_webhooks_list()
    assert type(res_list) == list

    res_show = mk_cli_admin.i_webhooks_show(
        res_create['id'],
    )
    assert type(res_show) == dict

    res_update = mk_cli_admin.i_webhooks_update(
        webhook_id=res_create['id'],
        name='test-webhook-renamed',
        url='test-webhook-renamed',
        secret='test-webhook-renamed',
        on=['mention', 'follow'],
        active=False,
    )
    assert type(res_update) == bool
    assert res_update

    res_delete = mk_cli_admin.i_webhooks_delete(
        res_create['id']
    )
    assert type(res_delete) == bool
    assert res_delete


def test_users_show(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users_show(
        username='user',
    )
    assert type(res) == dict


def test_users_following(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users_following(
        username='user'
    )
    assert type(res) == list


def test_users_followers(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users_followers(
        username='user'
    )
    assert type(res) == list


def test_user_notes(
    mk_cli_admin: Misskey,
    mk_admin_id: str,
):
    res = mk_cli_admin.users_notes(
        mk_admin_id,
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now()
        ),
    )
    assert type(res) == list


def test_users_stats(
    mk_cli_admin: Misskey,
    mk_admin_id: str,
):
    res = mk_cli_admin.users_stats(
        mk_admin_id,
    )
    assert type(res) == dict


def test_user_relation(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_single = mk_cli_admin.users_relation(
        mk_user_id,
    )
    assert type(res_single) == dict
    res_multiple = mk_cli_admin.users_relation(
        [mk_user_id],
    )
    assert type(res_multiple) == list


def test_following(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_follow = mk_cli_admin.following_create(
        mk_user_id,
    )
    assert type(res_follow) == dict
    res_unfollow = mk_cli_admin.following_delete(
        mk_user_id,
    )
    assert type(res_unfollow) == dict


def test_following_invalidate(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
    mk_admin_id: str,
    mk_user_id: str,
):
    res_follow = mk_cli_admin.following_create(
        mk_user_id,
    )
    assert type(res_follow) == dict

    res_invalidate = mk_cli_user.following_invalidate(
        mk_admin_id,
    )
    assert type(res_invalidate) == dict


def test_follow_request(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
    mk_user_id: str,
    mk_admin_id: str,
):
    mk_cli_user.i_update(
        is_locked=True,
    )
    mk_cli_admin.following_create(
        mk_user_id,
    )
    res_follow_cancel = mk_cli_admin.following_requests_cancel(
        mk_user_id,
    )
    assert type(res_follow_cancel) == dict

    mk_cli_admin.following_create(
        mk_user_id,
    )
    res_follow_list = mk_cli_user.following_requests_list()
    assert type(res_follow_list) == list
    res_follow_reject = mk_cli_user.following_requests_reject(
        mk_admin_id,
    )
    assert type(res_follow_reject) == bool
    assert res_follow_reject

    mk_cli_admin.following_create(
        mk_user_id,
    )
    res_follow_accept = mk_cli_user.following_requests_accept(
        mk_admin_id,
    )
    assert type(res_follow_accept) == bool
    assert res_follow_accept

    mk_cli_user.i_update(
        is_locked=False,
    )
    mk_cli_admin.following_delete(
        mk_user_id,
    )


def test_should_fail_in_drives_files_create(
    mk_cli_anon: Misskey
):
    with pytest.raises(MisskeyAPIException):
        with open('tests/test_image.png', mode='rb') as f:
            mk_cli_anon.drive_files_create(
                f,
            )


def test_drive(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.drive()
    assert type(res) == dict


def test_drive_stream(
    mk_cli_admin: Misskey,
):
    res_stream = mk_cli_admin.drive_stream()
    assert type(res_stream) == list

    res_files = mk_cli_admin.drive_files()
    assert type(res_files) == list

    res_folders = mk_cli_admin.drive_folders()
    assert type(res_folders) == list


def test_drive_files(
    mk_cli_admin: Misskey
):
    with open('tests/test_image.png', mode='rb') as f:
        res_create = mk_cli_admin.drive_files_create(
            f,
        )
        assert type(res_create) == dict

        res_file_check = mk_cli_admin.drive_files_check_existence(
            res_create['md5'],
        )
        assert type(res_file_check) == bool
        assert res_file_check

        res_find = mk_cli_admin.drive_files_find(
            res_create['name'],
        )
        assert type(res_find) == list

        res_find_hash = mk_cli_admin.drive_files_find_by_hash(
            res_create['md5'],
        )
        assert type(res_find_hash) == list

        res_attached_notes = mk_cli_admin.drive_files_attached_notes(
            res_create['id'],
        )
        assert type(res_attached_notes) == list

        res_files_show = mk_cli_admin.drive_files_show(
            res_create['id'],
        )
        assert type(res_files_show) == dict

        res_files_update = mk_cli_admin.drive_files_update(
            res_create['id'],
            folder_id=None,
            comment='test file',
        )
        assert type(res_files_update) == dict

        res_delete = mk_cli_admin.drive_files_delete(
            res_create['id'],
        )
        assert type(res_delete) == bool
        assert res_delete


def test_drive_files_upload_from_url(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.drive_files_upload_from_url(
        'https://placehold.jp/150x150.png',
    )
    assert type(res) == bool
    assert res


def test_drive_folders(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.drive_folders_create(
        name='test-folder',
    )
    assert type(res_create) == dict

    res_find = mk_cli_admin.drive_folders_find(
        name='test-folder'
    )
    assert type(res_find) == list

    res_show = mk_cli_admin.drive_folders_show(
        res_create['id'],
    )
    assert type(res_show) == dict

    res_update = mk_cli_admin.drive_folders_update(
        folder_id=res_create['id'],
        name='renamed-folder',
        parent_id=None,
    )
    assert type(res_update) == dict

    res_delete = mk_cli_admin.drive_folders_delete(
        res_create['id'],
    )
    assert type(res_delete) == bool
    assert res_delete


def test_users_report_abuse(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res = mk_cli_admin.users_report_abuse(
        user_id=mk_user_id,
        comment='this is test report abuse',
    )
    assert type(res) == bool
    assert res


def test_users_clips(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res = mk_cli_admin.users_clips(
        user_id=mk_user_id,
    )
    assert type(res) == list


def test_users(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.users(
        origin='combined',
        sort_key='updatedAt',
        hostname=TEST_HOST,
    )
    assert type(res) == list


def test_users_gallery_posts(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res = mk_cli_admin.users_gallery_posts(mk_user_id)
    assert type(res) == list


def test_users_get_freq(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res = mk_cli_admin.users_get_frequently_replied_users(mk_user_id)
    assert type(res) == list


def test_users_pages(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_pages = mk_cli_admin.users_pages(mk_user_id)
    assert type(res_pages) == list


def test_users_reactions(
    mk_cli_admin: Misskey,
    mk_admin_id: str,
):
    res_reactions = mk_cli_admin.users_reactions(
        user_id=mk_admin_id,
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now()
        ),
    )
    assert type(res_reactions) == list


def test_users_search(
    mk_cli_admin: Misskey,
):
    res_search = mk_cli_admin.users_search(
        query='user',
        origin='local',
    )
    assert type(res_search) == list

    res_by_username_and_host = mk_cli_admin.users_search_by_username_and_host(
        username='user',
        host=TEST_HOST,
    )
    assert type(res_by_username_and_host) == list


def test_email_address_available(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.email_address_available('test@example.com')
    assert type(res) == dict


def test_pinned_users(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.pinned_users()
    assert type(res) == list


def test_username_available(
    mk_cli_admin: Misskey,
):
    res = mk_cli_admin.username_available('user')
    assert type(res) == dict


def test_mute(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_mute = mk_cli_admin.mute_create(
        mk_user_id,
        expires_at=datetime.datetime.now() + datetime.timedelta(days=1)
    )
    assert type(res_mute) == bool
    assert res_mute

    res_mute_list = mk_cli_admin.mute_list()
    assert type(res_mute_list) == list

    res_unmute = mk_cli_admin.mute_delete(
        mk_user_id,
    )
    assert type(res_unmute) == bool
    assert res_unmute


def test_blocking(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_block = mk_cli_admin.blocking_create(
        mk_user_id,
    )
    assert type(res_block) == dict

    res_block_list = mk_cli_admin.blocking_list()
    assert type(res_block_list) == list

    res_unblock = mk_cli_admin.blocking_delete(
        mk_user_id,
    )
    assert type(res_unblock) == dict


def test_users_lists(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_create = mk_cli_admin.users_lists_create(
        'test-list',
    )
    assert type(res_create) == dict

    res_show = mk_cli_admin.users_lists_show(
        res_create['id'],
    )
    assert type(res_show) == dict

    res_list = mk_cli_admin.users_lists_list()
    assert type(res_list) == list

    res_push = mk_cli_admin.users_lists_push(
        list_id=res_create['id'],
        user_id=mk_user_id,
    )
    assert type(res_push) == bool
    assert res_push

    res_pull = mk_cli_admin.users_lists_pull(
        list_id=res_create['id'],
        user_id=mk_user_id,
    )
    assert type(res_pull) == bool
    assert res_pull

    res_update = mk_cli_admin.users_lists_update(
        list_id=res_create['id'],
        name='test-list-renamed',
    )
    assert type(res_update) == dict

    res_delete = mk_cli_admin.users_lists_delete(
        res_create['id'],
    )
    assert type(res_delete) == bool
    assert res_delete


def test_antennas(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.antennas_create(
        name='test-antenna',
        src='all',
    )
    assert type(res_create) == dict

    res_update = mk_cli_admin.antennas_update(
        res_create['id'],
        name='test-antenna-renamed',
        src='home',
    )
    assert type(res_update) == dict

    res_list = mk_cli_admin.antennas_list()
    assert type(res_list) == list

    res_notes = mk_cli_admin.antennas_notes(
        res_create['id'],
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now()
        ),
    )
    assert type(res_notes) == list

    res_show = mk_cli_admin.antennas_show(res_create['id'])
    assert type(res_show == dict)

    res_delete = mk_cli_admin.antennas_delete(
        antenna_id=res_create['id']
    )
    assert type(res_delete) == bool
    assert res_delete


def test_channels(
    mk_cli_admin: Misskey,
):
    res_create = mk_cli_admin.channels_create('test-channel')
    assert type(res_create) == dict

    res_notes_create = mk_cli_admin.notes_create(
        'post to test channel',
        channel_id=res_create['id'],
    )
    assert type(res_notes_create) == dict

    res_featured = mk_cli_admin.channels_featured()
    assert type(res_featured) == list

    res_follow = mk_cli_admin.channels_follow(res_create['id'])
    assert type(res_follow) == bool
    assert res_follow

    res_followed = mk_cli_admin.channels_followed()
    assert type(res_followed) == list

    res_owned = mk_cli_admin.channels_owned()
    assert type(res_owned) == list

    res_show = mk_cli_admin.channels_show(res_create['id'])
    assert type(res_show) == dict

    res_timeline = mk_cli_admin.channels_timeline(
        res_create['id'],
        since_date=(
            datetime.datetime.now() -
            datetime.timedelta(days=1)
        ),
        until_date=(
            datetime.datetime.now()
        ),
    )
    assert type(res_timeline) == list

    res_unfollow = mk_cli_admin.channels_unfollow(res_create['id'])
    assert type(res_unfollow) == bool
    assert res_unfollow

    res_update = mk_cli_admin.channels_update(
        res_create['id'],
        name='test-channel-renamed'
    )
    assert type(res_update) == dict


def test_charts(
    mk_cli_admin: Misskey,
):
    res_active_users = mk_cli_admin.charts_active_users(span='day')
    assert type(res_active_users) == dict

    res_ap_request = mk_cli_admin.charts_ap_request(span='day')
    assert type(res_ap_request) == dict

    res_drive = mk_cli_admin.charts_drive(span='day')
    assert type(res_drive) == dict

    res_federation = mk_cli_admin.charts_federation(span='hour', offset=30)
    assert type(res_federation) == dict

    res_instance = mk_cli_admin.charts_instance(host=TEST_HOST, span='hour')
    assert type(res_instance) == dict

    res_notes = mk_cli_admin.charts_notes(span='hour')
    assert type(res_notes) == dict

    res_users = mk_cli_admin.charts_users(span='hour')
    assert type(res_users) == dict


def test_charts_user(
    mk_cli_admin: Misskey,
    mk_user_id: str,
):
    res_drive = mk_cli_admin.charts_user_drive(mk_user_id, span='day')
    assert type(res_drive) == dict

    res_following = mk_cli_admin.charts_user_following(mk_user_id, span='day')
    assert type(res_following) == dict

    res_notes = mk_cli_admin.charts_user_notes(mk_user_id, span='day')
    assert type(res_notes) == dict

    res_pv = mk_cli_admin.charts_user_pv(mk_user_id, span='hour')
    assert type(res_pv) == dict

    res_reactions = mk_cli_admin.charts_user_reactions(mk_user_id, span='hour')
    assert type(res_reactions) == dict


def test_clips(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str,
):
    res_create = mk_cli_admin.clips_create(
        'test-clip',
        description='test clip description',
    )
    assert type(res_create) == dict

    res_add_note = mk_cli_admin.clips_add_note(
        clip_id=res_create['id'],
        note_id=mk_admin_new_note,
    )
    assert type(res_add_note) == bool
    assert res_add_note

    res_list = mk_cli_admin.clips_list()
    assert type(res_list) == list

    res_notes = mk_cli_admin.clips_notes(res_create['id'])
    assert type(res_notes) == list

    res_remove_note = mk_cli_admin.clips_remove_note(
        clip_id=res_create['id'],
        note_id=mk_admin_new_note,
    )
    assert type(res_remove_note) == bool
    assert res_remove_note

    res_show = mk_cli_admin.clips_show(res_create['id'])
    assert type(res_show) == dict

    res_update = mk_cli_admin.clips_update(
        res_create['id'],
        name='test-clip-renamed'
    )
    assert type(res_update) == dict

    res_delete = mk_cli_admin.clips_delete(res_create['id'])
    assert type(res_delete) == bool
    assert res_delete


def test_flash(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    res_create = mk_cli_admin.flash_create(
        title='test-play',
        summary='Hello world!',
        script='Ui:render([Ui:C:text({ text: "Hello world!" })])'
    )
    assert type(res_create) == dict

    res_featured = mk_cli_admin.flash_featured()
    assert type(res_featured) == list

    res_like = mk_cli_user.flash_like(res_create['id'])
    assert type(res_like) == bool
    assert res_like

    res_my = mk_cli_admin.flash_my()
    assert type(res_my) == list

    res_my_likes = mk_cli_user.flash_my_likes()
    assert type(res_my_likes) == list

    res_show = mk_cli_admin.flash_show(res_create['id'])
    assert type(res_show) == dict

    res_unlike = mk_cli_user.flash_unlike(res_create['id'])
    assert type(res_unlike) == bool

    res_update = mk_cli_admin.flash_update(
        flash_id=res_create['id'],
        title='test-play-renamed',
        summary='',
        script='',
    )
    assert type(res_update) == bool

    res_delete = mk_cli_admin.flash_delete(res_create['id'])
    assert type(res_delete) == bool
    assert res_delete


def test_gallery(
    mk_cli_admin: Misskey,
):
    res_featured = mk_cli_admin.gallery_featured()
    assert type(res_featured) == list

    res_popular = mk_cli_admin.gallery_popular()
    assert type(res_popular) == list

    res_posts = mk_cli_admin.gallery_posts()
    assert type(res_posts) == list


def test_gallery_posts(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    with open('tests/test_image.png', mode='rb') as f:
        res_files_create = mk_cli_admin.drive_files_create(f)
    assert type(res_files_create) == dict

    res_create = mk_cli_admin.gallery_posts_create(
        title='test-post',
        file_ids=[res_files_create['id']],
    )
    assert type(res_create) == dict

    res_like = mk_cli_user.gallery_posts_like(res_create['id'])
    assert type(res_like) == bool
    assert res_like

    res_show = mk_cli_admin.gallery_posts_show(res_create['id'])
    assert type(res_show) == dict

    res_unlike = mk_cli_user.gallery_posts_unlike(res_create['id'])
    assert type(res_unlike) == bool
    assert res_unlike

    res_update = mk_cli_admin.gallery_posts_update(
        post_id=res_create['id'],
        title='test-post-renamed',
        file_ids=[res_files_create['id']]
    )
    assert type(res_update) == dict

    res_delete = mk_cli_admin.gallery_posts_delete(res_create['id'])
    assert type(res_delete) == bool
    assert res_delete


def test_hashtags(
    mk_cli_admin: Misskey,
):
    res_update = mk_cli_admin.i_update(
        description='#test_tag',
    )
    assert type(res_update) == dict

    res_list = mk_cli_admin.hashtags_list(
        sort_key='attachedUsers'
    )
    assert type(res_list) == list

    res_search = mk_cli_admin.hashtags_search('test_tag')
    assert type(res_search) == list

    res_show = mk_cli_admin.hashtags_show('test_tag')
    assert type(res_show) == dict

    res_trend = mk_cli_admin.hashtags_trend()
    assert type(res_trend) == list

    res_users = mk_cli_admin.hashtags_users(
        'test_tag',
        origin='combined',
        sort_key='createdAt',
    )
    assert type(res_users) == list


def test_pages(
    mk_cli_admin: Misskey,
    mk_cli_user: Misskey,
):
    res_create = mk_cli_admin.pages_create(
        title='test-page',
        name='test-page',
    )
    assert type(res_create) == dict

    res_featured = mk_cli_admin.pages_featured()
    assert type(res_featured) == list

    res_like = mk_cli_user.pages_like(res_create['id'])
    assert type(res_like) == bool
    assert res_like

    res_show = mk_cli_admin.pages_show(res_create['id'])
    assert type(res_show) == dict

    res_unlike = mk_cli_user.pages_unlike(res_create['id'])
    assert type(res_unlike) == bool
    assert res_unlike

    res_update = mk_cli_admin.pages_update(
        page_id=res_create['id'],
        title='test-page-renamed',
        name='test-page-renamed',
    )
    assert type(res_update) == bool
    assert res_update

    res_delete = mk_cli_admin.pages_delete(res_create['id'])
    assert type(res_delete) == bool
    assert res_delete


def test_pages_create_with_content(
    mk_cli_admin: Misskey,
):
    with open('tests/test_image.png', mode='rb') as f:
        res_file = mk_cli_admin.drive_files_create(f)
    assert type(res_file) == dict

    res_sub = mk_cli_admin.pages_create(
        title='sub-page',
        name='sub-page',
        summary='sub summary',
        content=[{
            'type': 'text',
            'text': '\n'.join([str(i)*10 for i in range(10)])
        }],
    )
    assert type(res_sub) == dict

    main_content = [
        {
            'type': 'section',
            'title': 'section-title',
            'children': [
                {
                    'type': 'text',
                    'text': 'inside section',
                },
            ],
        },
        {
            'type': 'text',
            'text': 'outside section\n' 'a = {a}',
        },
        {
            'type': 'image',
            'fileId': res_file['id'],
        },
        {
            'type': 'note',
            'note': res_sub['id'],
            'detailed': True,
        },
    ]
    res_main = mk_cli_admin.pages_create(
        title='main page',
        name='main page',
        summary='main summary',
        content=main_content,
        script='<: "Hello, world!"',
        variables=[
            {
                'name': 'a',
                'type': 'number',
                'value': 1,
            }
        ],
        eye_catching_image_id=res_file['id'],
        font_serif=True,
        align_center=True,
        hide_title_when_pinned=True,
    )
    assert type(res_main) == dict

    mk_cli_admin.pages_delete(res_sub['id'])
    mk_cli_admin.pages_delete(res_main['id'])
    mk_cli_admin.drive_files_delete(res_file['id'])
