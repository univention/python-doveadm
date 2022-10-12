# -*- coding: utf-8 -*-

"""
doveadm - access the Doveadm HTTP API

(c) 2021 by Univention GmbH

License: TBD
"""

import time
import json
from base64 import b64encode
from typing import Optional

import requests

__all__ = (
    'DovAdm',
    'DovAdmCmd',
    'DovAdmError',
    'DovAdmResult',
)

DOVADM_ERROR_MSG = {
    2: 'Success but mailbox changed during operation',
    64: 'Invalid parameters',
    65: 'Data error',
    67: 'User does not exist',
    68: 'User does not have session',
    73: 'User quota is full',
    75: 'Temporary error',
    77: 'No permission',
    78: 'Invalid configuration',
}


class DovAdmResult:  # pylint: disable=too-few-public-methods
    """
    generic base class for response messages
    """

    __slots__ = (
        'rtype',
        'data',
        'tag',
    )

    rtype: str
    data: dict
    tag: str

    def __init__(self, payload):
        self.rtype, self.data, self.tag = payload

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(({self.rtype!r}, {self.data!r}, {self.tag!r}))'
        )


class DovAdmCmd:  # pylint: disable=too-few-public-methods
    """
    Base class for doveadm commands
    """

    res_class = DovAdmResult

    __slots__ = (
        '_command',
        '_params',
        'tag',
    )

    _command: str
    _params: dict
    tag: str

    def __init__(
        self,
        command: str,
        tag: Optional[str] = None,
        **params,
    ):
        self._command = command
        self._params = params
        self.tag = tag or f'tag-{time.time()}'

    @property
    def payload(self):
        """
        return JSON payload to be sent as-is to doveadm HTTP API
        """
        params = {}
        for key, val in (self._params or {}).items():
            if val is None:
                continue
            if isinstance(val, bool):
                val = str(val).lower()
            params[key] = val
        return json.dumps(
            # outer sequence with always one item
            (
                # inner sequence for the command tuple
                (
                    self._command,
                    params,
                    self.tag,
                ),
            ),
        )


class DovAdmError(Exception):
    """
    generic exception class for error response
    """

    __slots__ = (
        'rtype',
        'data',
        'tag',
    )

    rtype: str
    data: dict
    tag: str

    def __init__(
        self,
        response: Optional[DovAdmResult] = None,
        msg: Optional[str] = None,
    ):
        super().__init__()
        self._response = response
        self._msg = msg
        self.exit_code = self._response.data['exitCode']

    def __str__(self) -> str:
        return (
            f'doveadm error {self.exit_code:d}: '
            f'{DOVADM_ERROR_MSG.get(self.exit_code, "unknown")}'
        )

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}'
            f'(({self._response!r}, msg={self._msg!r}))'
        )


class DovAdm:
    """
    Class for connecting to Doveadm HTTP API with proper authentication
    """

    __slots__ = (
        '_url',
        '_authz',
    )

    _url: str
    _authz: bytes

    def __init__(
        self,
        url: str,
        username: str = 'doveadm',
        password: str = None,
        api_key: str = None,
    ):
        self._url = url
        # enforce using either one of the authentication methods
        if password is not None and api_key is not None:
            raise ValueError(
                'You must either use password or api_key, not both!'
            )
        # prepare the Authorization header value
        if password is not None:
            # generate HTTP basic authentication value
            _authz = b'Basic %s' % (
                b64encode(':'.join((username, password)).encode('utf-8')),
            )
        elif api_key is not None:
            # generate HTTP basic authentication value
            _authz = b'X-Dovecot-API %s' % (
                b64encode(api_key.encode('utf-8')),
            )
        else:
            raise ValueError(
                'Either password or api_key needed for authentication!'
            )
        self._authz = _authz.decode('ascii')

    @property
    def authorization(self):
        """
        returns value to be used for HTTP header 'Authorization'
        """
        return self._authz

    def submit(self, cmd: DovAdmCmd):
        """
        submit a single command to dovadm and return the result

        Note:
        In theory it is possible to send multiple commands in one HTTP request
        but doveadm docs explicitly recommend not to make use of that.
        """
        response = requests.post(
            self._url,
            headers=dict(Authorization=self.authorization),
            data=cmd.payload,
        )

        if response.status_code != 200:
            raise DovAdmError(
                msg=(
                    f'Web server replied with status-code '
                    f'{response.status_code}, got text {response.text!r}'
                )
            )
        try:
            content = response.json()
        except json.decoder.JSONDecodeError as err:
            raise DovAdmError(
                msg=(
                    f'Failed to parse JSON of web servers response, '
                    f'got text {response.text!r}'
                )
            ) from err
        result = cmd.res_class(content[0])

        if result.tag != cmd.tag:

            raise DovAdmError(
                msg=(
                    f'Expected request tag {result.tag!r} in result, '
                    f'got response tag {cmd.tag!r}'
                )
            )
        if result.rtype == 'error':
            raise DovAdmError(response=result)
        return result
