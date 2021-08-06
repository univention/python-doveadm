# -*- coding: utf-8 -*-
"""
doveadm.fs - file system commands

(c) 2021 by Univention GmbH

License: TBD
"""

from typing import Optional, Sequence

from . import DovAdmCmd, DovAdmResult

__all__ = (
    'FsDeleteCmd',
)


class FsDeleteCmd(DovAdmCmd):
    """
    https://doc.dovecot.org/admin_manual/doveadm_http_api/#doveadm-fs-delete
    """
    command = 'fsDelete'

    def __init__(
            self,
            path: Sequence[str],
            fs_driver: str = 'posix',
            fs_args: str = 'dirs',
            recursive: Optional[bool] = None,
            max_parallel: Optional[int] = None,
            tag: Optional[str] = None,
        ):
        DovAdmCmd.__init__(
            self,
            self.command,
            tag,
            **dict(
                path=path,
                fsDriver=fs_driver,
                fsArgs=fs_args,
                recursive=recursive,
                maxParallel=max_parallel,
            ),
        )
