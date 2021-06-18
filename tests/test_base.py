# -*- coding: utf-8 -*-
"""
basic tests which do not require running dovecot server
"""

import unittest

from doveadm import DovAdmCommand, DovAdm
from doveadm.mailbox import MailboxCreate, MailboxDelete, MailboxStatus


class Test001DovAdmCommand(unittest.TestCase):
    """
    test class doveadm.DovAdmCommand
    """

    def test_001_payload(self):
        self.assertEqual(
            DovAdmCommand(
                'reload',
                'tag1',
            ).payload,
            '[["reload", {}, "tag1"]]',
        )
        self.assertEqual(
            DovAdmCommand(
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
            '[["altmove", {"user": "samik", "reverse": 0, "query": ["mailbox", "INBOX/myfoldertoo", "savedbefore", "since", "30d"]}, "tag1"]]', 
        )


class Test001DovAdmCommand(unittest.TestCase):
    """
    test class doveadm.mailbox.MailboxCreate
    """

    def test000_mailbox_status(self):
        self.assertEqual(
            MailboxStatus(
                user='samik',
                field=['all'],
                mailbox_mask=[
                    "INBOX",
                    "INBOX/*",
                    "*",
                ],
                tag='tag1',
            ).payload,
            '[["mailboxStatus", {"user": "samik", "field": ["all"], "mailboxMask": ["INBOX", "INBOX/*", "*"]}, "tag1"]]',
        )

    def test001_mailbox_create(self):
        self.assertEqual(
            MailboxCreate(
                user='samik',
                mailbox=[
                    "INBOX/myfolder"
                ],
                tag='tag1',
            ).payload,
            '[["mailboxCreate", {"user": "samik", "mailbox": ["INBOX/myfolder"]}, "tag1"]]',
        )

    def test002_mailbox_delete(self):
        self.assertEqual(
            MailboxDelete(
                user='samik',
                mailbox=[
                    "INBOX/myfolder"
                ],
                tag='tag1',
            ).payload,
            '[["mailboxDelete", {"user": "samik", "mailbox": ["INBOX/myfolder"]}, "tag1"]]',
        )


class Test003AuthorizationHeader(unittest.TestCase):
    """
    test property doveadm.DovAdm.authorization
    """

    def test000_url(self):
          self.assertEqual(
              DovAdm('http://host:port/doveadm/v1', password='foo')._url,
              'http://host:port/doveadm/v1',
          )

    def test001_password(self):
          self.assertEqual(
              DovAdm('http://host:port/doveadm/v1', password='foo').authorization,
              'Basic ZG92ZWFkbTpmb28=',
          )
          self.assertEqual(
              DovAdm('http://host:port/doveadm/v1', username='foo', password='bar').authorization,
              'Basic Zm9vOmJhcg==',
          )

    def test002_api_key(self):
          self.assertEqual(
              DovAdm('http://host:port/doveadm/v1', api_key='012346789').authorization,
              'X-Dovecot-API MDEyMzQ2Nzg5',
          )

    def test003_value_error(self):
          with self.assertRaises(ValueError):
              DovAdm('http://host:port/doveadm/v1', password='foo', api_key='bar')


if __name__ == '__main__':
    unittest.main()
