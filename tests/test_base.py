# -*- coding: utf-8 -*-

"""
basic tests which do not require running dovecot server
"""

import unittest

from doveadm import DovAdmCmd, DovAdm
from doveadm.mailbox import (
    MailboxCreateCmd,
    MailboxDeleteCmd,
    MailboxStatusCmd,
)
from doveadm.fs import FsDeleteCmd
from doveadm.misc import WhoCmd


class Test001DovAdmCmd(unittest.TestCase):
    """
    test class doveadm.DovAdmCmd
    """
    def test_001_payload(self):
        """test DovAdmCmd"""
        self.assertEqual(
            DovAdmCmd(
                'reload',
                'tag1',
            ).payload,
            '[["reload", {}, "tag1"]]',
        )
        self.assertEqual(
            DovAdmCmd(
                'altmove',
                'tag1',
                user='samik',
                reverse=0,
                query=[
                    'mailbox',
                    'INBOX/myfoldertoo',
                    'savedbefore',
                    'since',
                    '30d',
                ],
            ).payload,
            (
                '[["altmove", {"user": "samik", "reverse": 0, '
                '"query": ["mailbox", "INBOX/myfoldertoo", "savedbefore", '
                '"since", "30d"]}, "tag1"]]'
            ),
        )


class Test002MailboxCmd(unittest.TestCase):
    """
    test class doveadm.mailbox.MailboxCreateCmd
    """
    def test000_mailbox_status(self):
        """test MailboxStatusCmd"""
        self.assertEqual(
            MailboxStatusCmd(
                user='samik',
                field=['all'],
                mailbox_mask=[
                    "INBOX",
                    "INBOX/*",
                    "*",
                ],
                tag='tag1',
            ).payload,
            (
                '[["mailboxStatus", {"user": "samik", "field": ["all"], '
                '"mailboxMask": ["INBOX", "INBOX/*", "*"]}, "tag1"]]'
            ),
        )

    def test001_mailbox_create(self):
        """test MailboxCreateCmd"""
        self.assertEqual(
            MailboxCreateCmd(
                user='samik',
                mailbox=["INBOX/myfolder"],
                tag='tag1',
            ).payload,
            (
                '[["mailboxCreate", {"user": "samik", '
                '"mailbox": ["INBOX/myfolder"]}, "tag1"]]'
            ),
        )

    def test002_mailbox_delete(self):
        """test MailboxDeleteCmd"""
        self.assertEqual(
            MailboxDeleteCmd(
                user='samik',
                mailbox=["INBOX/myfolder"],
                tag='tag1',
            ).payload,
            (
                '[["mailboxDelete", {"user": "samik", '
                '"mailbox": ["INBOX/myfolder"]}, "tag1"]]'
            ),
        )

    def test003_fs_delete(self):
        """test FsDeleteCmd"""
        self.assertEqual(
            FsDeleteCmd(
                path=[
                    '/path/to/vmail/samik',
                ],
                tag='tag1',
            ).payload,
            (
                '[["fsDelete", {"path": ["/path/to/vmail/samik"], '
                '"fsDriver": "posix", "fsArgs": "dirs"}, "tag1"]]'
            ),
        )
        self.assertEqual(
            FsDeleteCmd(
                path=[
                    '/path/to/vmail/samik',
                ],
                recursive=True,
                tag='tag1',
            ).payload,
            (
                '[["fsDelete", {"path": ["/path/to/vmail/samik"], '
                '"fsDriver": "posix", "fsArgs": "dirs", "recursive": 1}, '
                '"tag1"]]'
            ),
        )


class Test003AuthorizationHeader(unittest.TestCase):
    """
    test property doveadm.DovAdm.authorization
    """
    def test000_url(self):
        """test url of DovAdm"""
        self.assertEqual(
            DovAdm('http://host:port/doveadm/v1', password='foo')._url,  # noqa: E501; pylint: disable=protected-access
            'http://host:port/doveadm/v1',
        )

    def test001_password(self):
        """test basic-auth encoding of DovAdm"""
        self.assertEqual(
            DovAdm('http://host:port/doveadm/v1',
                   password='foo').authorization,
            'Basic ZG92ZWFkbTpmb28=',
        )
        self.assertEqual(
            DovAdm(
                'http://host:port/doveadm/v1', username='foo', password='bar'
            ).authorization,
            'Basic Zm9vOmJhcg==',
        )

    def test002_api_key(self):
        """test X-Dovecot-API with DovAdm"""
        self.assertEqual(
            DovAdm('http://host:port/doveadm/v1',
                   api_key='012346789').authorization,
            'X-Dovecot-API MDEyMzQ2Nzg5',
        )

    def test003_value_error(self):
        """test DovAdm for ValueError"""
        with self.assertRaises(ValueError):
            DovAdm(
                'http://host:port/doveadm/v1', password='foo', api_key='bar'
            )


class Test004WhoCmd(unittest.TestCase):
    """
    test class doveadm.misc.WhoCmd
    """
    def test000_who(self):
        """test the who request"""
        self.assertEqual(
            WhoCmd(tag='tag1', ).payload,
            '[["who", {}, "tag1"]]',
        )


if __name__ == '__main__':
    unittest.main()
