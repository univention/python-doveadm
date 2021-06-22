# -*- coding: utf-8 -*-
"""
doveadm.__about__ - Meta information

(c) 2021 by Univention GmbH

License: TBD
"""

import collections

VersionInfo = collections.namedtuple('VersionInfo', ('major', 'minor', 'micro'))
__version_info__ = VersionInfo(
    major=0,
    minor=0,
    micro=1,
)
__version__ = '.'.join(str(val) for val in __version_info__)
__author__ = 'Michael Stroeder'
__mail__ = 'michael@stroeder.com'
__copyright__ = '(c) 2021 by Univention GmbH'
__license__ = 'TBD'

__all__ = [
    '__version_info__',
    '__version__',
    '__author__',
    '__mail__',
    '__license__',
    '__copyright__',
]
