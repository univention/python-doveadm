# -*- coding: utf-8 -*-

"""
doveadm.fs - file system commands

(c) 2021 by Univention GmbH

License: TBD
"""

from typing import Optional, Sequence

from . import DovAdmCmd

__all__ = ('FsDeleteCmd', )


class FsDeleteCmd(DovAdmCmd):  # pylint: disable=too-few-public-methods
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
        super().__init__(  # pylint: disable=too-many-function-args
            self.command,
            tag,
            **{
                'path': path,
                'fsDriver': fs_driver,
                'fsArgs': fs_args,
                'recursive': recursive,
                'maxParallel': max_parallel,
            },
        )
