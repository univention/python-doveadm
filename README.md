python-doveadm - Using Doveadm HTTP API with Python
===================================================

Convenience module for using the
[Doveadm HTTP API](https://doc.dovecot.org/admin_manual/doveadm_http_api/)
to manage Dovecot mailbox users.

Notes:

   * While the Doveadm HTTP API supports sending multiple commands at
     once this is not recommended and thus this module only sends
     single commands in a POST request
   * Error responses are turned into DovAdmError exceptions.
   * Currently only implements create/rename/delete for mailboxes.

Running automated tests
-----------------------

For running the tests a local dovecot server executable has to be available
which is by default expected at /usr/sbin/dovecot.

On Debian buster install dovecot with IMAP service:

```
apt install -y dovecot-imapd dovecot-pop3d dovecot-lmtpd
```

After that you can invoke the tests from within the source directory:

```
python3 -B -m unittest -v
```
