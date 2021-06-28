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
import imaplib

from doveadm import DovAdmCmd, DovAdm, DovAdmError
from doveadm.mailbox import (
    MailboxCreateCmd,
    MailboxDeleteCmd,
    MailboxStatusCmd,
)
from doveadm.fs import FsDeleteCmd
from doveadm.misc import WhoCmd

DOVECOT_CONF_TMPL = os.environ.get(
    'DOVECOT_CONF_TMPL',
    os.path.join('tests', 'conf', 'dovecot.conf.tmpl')
)
DOVE_EXEC = os.environ.get('DOVE_EXEC', '/usr/sbin/dovecot')

# we have to use non-privileged ports
DOVECOT_POP3_PORT = 10110
DOVECOT_IMAP_PORT = 10143
DOVEADM_PORT = 8080
DOVEADM_URI = 'http://localhost:{:d}/doveadm/v1'.format(DOVEADM_PORT)

DOVEADM_USERNAME = 'doveadm'
DOVEADM_PASSWORD = 'secretpassword'
DOVEADM_API_KEY = 'secretkey'

DOVECOT_USER_PASSWORD = 'hmpf-ganz-sicher-hmpf'


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
                    imap_port=DOVECOT_IMAP_PORT,
                    pop3_port=DOVECOT_POP3_PORT,
                    passdb_password=DOVECOT_USER_PASSWORD,
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
        reload_cmd = DovAdmCmd('reload', tag='tag1')
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

    def test000_imap_login(self):
        """
        only test a dummy IMAP login with username and password
        and send who request
        """
        dov_adm = DovAdm(DOVEADM_URI, api_key=DOVEADM_API_KEY)
        with imaplib.IMAP4('127.0.0.1', port=DOVECOT_IMAP_PORT) as imap_conn:
            imap_conn.login('samik', DOVECOT_USER_PASSWORD)
            ityp, mbox_lst = imap_conn.list()
            res1 = dov_adm.submit(WhoCmd(separate=True, tag='tag1'))
            res2 = dov_adm.submit(WhoCmd(tag='tag2'))
        self.assertEqual(ityp, 'OK')
        self.assertEqual(mbox_lst, [b'(\\HasNoChildren) "/" INBOX'])
        self.assertEqual(res1.rtype, 'doveadmResponse')
        self.assertEqual(res1.data[0]['connections'], '1')
        self.assertEqual(res1.data[0]['ips'], '(127.0.0.1)')
        self.assertEqual(res1.data[0]['username'], 'samik')
        self.assertEqual(res1.usernames, ['samik'])
        self.assertEqual(res1.tag, 'tag1')
        self.assertEqual(res2.rtype, 'doveadmResponse')
        self.assertEqual(res2.data[0]['connections'], '1')
        self.assertEqual(res2.data[0]['ips'], '(127.0.0.1)')
        self.assertEqual(res2.data[0]['username'], 'samik')
        self.assertEqual(res2.usernames, ['samik'])
        self.assertEqual(res2.tag, 'tag2')

    def test001_mailbox_commands(self):
        """
        send CRUD operations on an example mailbox
        """
        dov_adm = DovAdm(DOVEADM_URI, api_key=DOVEADM_API_KEY)
        vmail_subdirs = (self.vmail_dir, 'samik', 'mdbox', 'mailboxes', 'INBOX', 'folder1')
        mbox_names = (
            'INBOX',
            'INBOX/folder1',
            'INBOX/folder2',
        )
        mbox_create_cmd = MailboxCreateCmd(
            user='samik',
            mailbox=mbox_names,
            tag='tag1',
        )
        mbox_status_cmd = MailboxStatusCmd(
            user='samik',
            field=['all'],
            mailbox_mask=[
                'INBOX',
                'INBOX/*',
                '*',
            ],
            tag='tag2',
        )
        mbox_delete_cmd = MailboxDeleteCmd(
            user='samik',
            mailbox=mbox_names,
            tag='tag3',
        )
        fs_delete_cmd = FsDeleteCmd(
            path=[os.path.join(*vmail_subdirs[0:2])],
            recursive=True,
            tag='tag4',
        )
        # create a new mailbox
        res = dov_adm.submit(mbox_create_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag1')
        self.assertTrue(os.path.isdir(os.path.join(*vmail_subdirs)))
        # query status of created mailbox
        res = dov_adm.submit(mbox_status_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.tag, 'tag2')
        self.assertEqual(set(res.mailboxes), set(mbox_names))
        # list mailboxes via IMAPresults
        with imaplib.IMAP4('127.0.0.1', port=DOVECOT_IMAP_PORT) as imap_conn:
            imap_conn.login('samik', DOVECOT_USER_PASSWORD)
            ityp, mbox_lst = imap_conn.list()
        self.assertEqual(ityp, 'OK')
        self.assertEqual(
            sorted(mbox_lst),
            sorted([
                b'(\\HasChildren) "/" INBOX',
                b'(\\HasNoChildren) "/" INBOX/folder1',
                b'(\\HasNoChildren) "/" INBOX/folder2',
            ])
        )
        # re-create a new mailbox must fail
        with self.assertRaises(DovAdmError) as ctx:
            res = dov_adm.submit(mbox_create_cmd)
        self.assertEqual(ctx.exception.exit_code, 65)
        self.assertEqual(str(ctx.exception), 'doveadm error 65: Data error')
        # delete created mailbox
        res = dov_adm.submit(mbox_delete_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag3')
        self.assertFalse(os.path.isdir(os.path.join(*vmail_subdirs[0:-1])))
        # deleting same mailbox again must fail
        with self.assertRaises(DovAdmError) as ctx:
            res = dov_adm.submit(mbox_delete_cmd)
        self.assertEqual(ctx.exception.exit_code, 68)
        self.assertEqual(str(ctx.exception), 'doveadm error 68: User does not have session')
        # list mailboxes via IMAP should return no results
        with imaplib.IMAP4('127.0.0.1', port=DOVECOT_IMAP_PORT) as imap_conn:
            imap_conn.login('samik', DOVECOT_USER_PASSWORD)
            ityp, mbox_lst = imap_conn.list()
        self.assertEqual(ityp, 'OK')
        self.assertEqual(mbox_lst, [b'(\\HasNoChildren) "/" INBOX'])
        # delete the whole user directory
        res = dov_adm.submit(fs_delete_cmd)
        self.assertEqual(res.rtype, 'doveadmResponse')
        self.assertEqual(res.data, [])
        self.assertEqual(res.tag, 'tag4')
        self.assertFalse(os.path.isdir(os.path.join(*vmail_subdirs[0:2])))


if __name__ == '__main__':
    unittest.main()
