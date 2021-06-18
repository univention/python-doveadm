# -*- coding: utf-8 -*-
"""
doveadm.mailbox - mailbox commands

(c) 2021 by Univention GmbH

License: TBD
"""

from typing import Optional, Sequence

from . import DovAdmCommand

__all__ = (
    'MailboxCreate',
    'MailboxDelete',
)


class MailboxCreate(DovAdmCommand):
    """
    https://doc.dovecot.org/admin_manual/doveadm_http_api/#doveadm-mailbox-create
    """
    command = 'mailboxCreate'

    def __init__(
            self,
            user: str,
            guid: Optional[str] = None,
            mailbox: Optional[Sequence[str]] = None,
            tag: Optional[str] = None,
        ):
        DovAdmCommand.__init__(
            self,
            self.command,
            tag,
            **dict(
                user=user,
                guid=guid,
                mailbox=mailbox,
            ),
        )


class MailboxDelete(DovAdmCommand):
    """
    https://doc.dovecot.org/admin_manual/doveadm_http_api/#doveadm-mailbox-delete
    """
    command = 'mailboxDelete'

    def __init__(
            self,
            user: str,
            require_empty: Optional[bool] = None,
            recursive: Optional[bool] = None,
            unsafe: Optional[bool] = None,
            mailbox: Optional[Sequence[str]] = None,
            tag: Optional[str] = None,
        ):
        DovAdmCommand.__init__(
            self,
            self.command,
            tag,
            **dict(
                user=user,
                requireEmpty=require_empty,
                recursive=recursive,
                unsafe=unsafe,
                mailbox=mailbox,
            ),
        )
