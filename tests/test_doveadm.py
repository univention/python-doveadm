# -*- coding: utf-8 -*-
"""
tests herein require running dovecot server
"""

import os
import os.path
import unittest
import subprocess
import logging
import pwd
import grp
import time

from doveadm import DovAdmCommand, DovAdm, DovAdmError
from doveadm.mailbox import (
    MailboxCreate,
    MailboxDelete,
    MailboxStatus,
)

DOVECOT_CONF_TMPL = os.environ.get(
    'DOVECOT_CONF_TMPL',
    os.path.join('tests', 'conf', 'dovecot.conf.tmpl')
)
DOVE_EXEC = os.environ.get('DOVE_EXEC', '/usr/sbin/dovecot')


DOVEADM_PORT = 8080
DOVEADM_URI = 'http://localhost:{:d}/doveadm/v1'.format(DOVEADM_PORT)

DOVEADM_USERNAME = 'doveadm'
DOVEADM_PASSWORD = 'secretpassword'
DOVEADM_API_KEY = 'secretkey'


logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'INFO').upper())


class TestDovAdm(unittest.TestCase):
    """
    test class doveadm.DovAdm
    """

    def _cleanup(self):
        """
        Recursively delete whole directory
        """
        if not os.path.exists(self.base_dir):
            return
        logging.debug('cleaning up %s ...', self.base_dir)
        for dirpath, dirnames, filenames in os.walk(
                self.base_dir,
                topdown=False
            ):
            for filename in filenames:
                logging.debug('remove %s', os.path.join(dirpath, filename))
                os.remove(os.path.join(dirpath, filename))
            for dirname in dirnames:
                logging.debug('rmdir %s', os.path.join(dirpath, dirname))
                os.rmdir(os.path.join(dirpath, dirname))
        os.rmdir(self.base_dir)

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.join(
            os.environ.get('TMP', '/tmp'),
            'dovecot-test-{:d}'.format(os.getpid()),
        )
        logging.debug('cls.base_dir = %r', cls.base_dir)
        state_dir = os.path.join(cls.base_dir, 'state')
        cls.vmail_dir = os.path.join(cls.base_dir, 'vmail')
        mail_temp_dir = os.path.join(cls.base_dir, 'tmp')
        for dirname in (
                cls.base_dir,
                state_dir,
                cls.vmail_dir,
                mail_temp_dir,
            ):
            if not os.path.isdir(dirname):
                os.mkdir(dirname, mode=0o0755)
        log_path = os.path.join(cls.base_dir, 'dovecot.log')
        config_path = os.path.join(cls.base_dir, 'dovecot.conf.generated')
        with open(DOVECOT_CONF_TMPL, 'r') as tmpl_file:
            tmpl_str = tmpl_file.read()
        with open(config_path, 'w') as config_file:
            config_file.write(
                tmpl_str.format(
                    base_dir=cls.base_dir,
                    log_path=log_path,
                    state_dir=state_dir,
                    vmail_dir=cls.vmail_dir,
                    mail_temp_dir=mail_temp_dir,
                    doveadm_port=DOVEADM_PORT,
                    user=pwd.getpwuid(os.getuid()).pw_name,
                    group=grp.getgrgid(os.getgid()).gr_name,
                )
            )
        dovecot_cmd = (DOVE_EXEC, '-F', '-c', config_path)
        cls._proc = subprocess.Popen(dovecot_cmd)
        time.sleep(1.0)
        if cls._proc.poll() is not None:
            raise RuntimeError('dovecot exited before opening port')
        logging.debug('Started dovecot server with %r', dovecot_cmd)

    @classmethod
    def tearDownClass(cls):
        cls._proc.terminate()
        cls._proc.wait()
        cls._cleanup(cls)

    def test000_reload(self):
        """
        use a simple reload command to test basic authc and API key
        """
        reload_cmd = DovAdmCommand('reload', tag='tag1')
        dov_adm = DovAdm(DOVEADM_URI, username=DOVEADM_USERNAME, password=DOVEADM_PASSWORD)
        res = dov_adm.submit(reload_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag1')
        dov_adm = DovAdm(DOVEADM_URI, api_key=DOVEADM_API_KEY)
        res = dov_adm.submit(reload_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag1')

    def test001_mailbox_commands(self):
        """
        send CRUD operations on an example mailbox
        """
        dov_adm = DovAdm(DOVEADM_URI, api_key=DOVEADM_API_KEY)
        vmail_folder_path = os.path.join(self.vmail_dir, 'samik', 'mdbox', 'mailboxes', 'INBOX', 'myfolder')
        mbox_create_cmd = MailboxCreate(
            user='samik',
            mailbox=[
                "INBOX/myfolder"
            ],
            tag='tag1',
        )
        mbox_status_cmd = MailboxStatus(
            user='samik',
            field=['all'],
            mailbox_mask=[
                'INBOX',
                'INBOX/*',
                '*',
            ],
            tag='tag2',
        )
        mbox_delete_cmd = MailboxDelete(
            user='samik',
            mailbox=[
                "INBOX/myfolder"
            ],
            tag='tag3',
        )
        res = dov_adm.submit(mbox_create_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag1')
        self.assertTrue(os.path.isdir(vmail_folder_path))
        res = dov_adm.submit(mbox_status_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.tag, 'tag2')
        self.assertEqual(
            {mbox_dat['mailbox'] for mbox_dat in res.data},
            {'INBOX', 'INBOX/myfolder'}
        )
        with self.assertRaises(DovAdmError) as ctx:
            res = dov_adm.submit(mbox_create_cmd)
        self.assertEqual(ctx.exception.exit_code, 65)
        self.assertEqual(str(ctx.exception), 'doveadm error 65: Data error')
        res = dov_adm.submit(mbox_delete_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag3')
        self.assertFalse(os.path.isdir(vmail_folder_path))
        with self.assertRaises(DovAdmError) as ctx:
            res = dov_adm.submit(mbox_delete_cmd)
        self.assertEqual(ctx.exception.exit_code, 68)
        self.assertEqual(str(ctx.exception), 'doveadm error 68: User does not have session')
        res = dov_adm.submit(mbox_status_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        # TODO: find out whether that's the right result
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.tag, 'tag2')


if __name__ == '__main__':
    unittest.main()
