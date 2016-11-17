# -*- coding: utf-8 -*-
import os
import yaml
import base64
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging


class SecuredRepoMgr(object):
    """
    Secured Repository Manager
    This class provides secured management of configuration files for
    automated provisioning (e.g. Playground Template, Box Configuration file)
    and DsP-Installer's Operation.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SecuredRepoMgr, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._seckey = None
        self._secseed = None
        self._secure_mode = None

        self._logger = logging.getLogger("SecuredRepositoryManager")
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fm)
        self._logger.addHandler(ch)

    def initialize(self, __salt, __is_secure=False):
        if __is_secure:
            self.load_seckey(__salt)
            self._secure_mode = __is_secure

    def load_seckey(self, salt):
        self._secseed = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        p = raw_input("Input the password for secured repository: ")
        self._seckey = base64.urlsafe_b64encode(kdf.derive(p))

    def read_file(self, __file_path):
        if self._secure_mode:
            self._logger.debug("Enter the read_file with secure mode")
            return self._read_encrypt_file(__file_path)
        else:
            rf = open(__file_path, 'r')
            l = rf.read(-1)
            rf.close()
            return l

    def _read_encrypt_file(self, __encrypt_file_path):
        rf = open(__encrypt_file_path, 'r')
        l = rf.read(-1)
        rf.close()
        f = Fernet(self._seckey)
        try:
            return f.decrypt(l)
        except cryptography.fernet.InvalidToken:
            self._logger.error("Password or Salt is not correct.")
            return None

    def _write_encrypt_file(self, __encrypt_file_path, __plain_text):
        wf = open(__encrypt_file_path, 'w')
        f = Fernet(self._seckey)
        wf.write((f.encrypt(__plain_text)))
        wf.close()

    def encrypt_file(self, org_file_path, enc_file_path):
        rf = open(org_file_path, 'r')
        l = rf.read(-1)
        rf.close()
        self._write_encrypt_file(enc_file_path, l)

    def decrypt_file(self, enc_file_path, dec_file_path):
        wf = open(dec_file_path, 'w')
        wf.write(self._read_encrypt_file(enc_file_path))
        wf.close()


if __name__ == "__main__":
    sr = SecuredRepoMgr()
    ts = os.urandom(16)
    sr.load_seckey(ts)
