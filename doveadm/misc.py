# -*- coding: utf-8 -*-

"""
doveadm.misc - various commands

(c) 2021 by Univention GmbH

License: TBD
"""

from typing import Optional, Sequence

from . import DovAdmCmd, DovAdmResult

__all__ = ('WhoCmd', )


class WhoResult(DovAdmResult):  # pylint: disable=too-few-public-methods
    """
    result class for
    https://doc.dovecot.org/admin_manual/doveadm_http_api/#doveadm-who
    """
    @property
    def usernames(self) -> Sequence[str]:
        """return usernames from results"""
        return [who['username'] for who in self.data]


class WhoCmd(DovAdmCmd):  # pylint: disable=too-few-public-methods
    """
    request class for
    https://doc.dovecot.org/admin_manual/doveadm_http_api/#doveadm-who
    """

    command = 'who'
    res_class = WhoResult

    def __init__(
        self,
        mask: Optional[str] = None,
        separate: Optional[bool] = None,
        tag: Optional[str] = None,
    ):
        DovAdmCmd.__init__(
            self,
            self.command,
            tag,
            **dict(
                mask=mask,
                separateConnections=separate,
            ),
        )
