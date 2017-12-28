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


class StoreManager(object):
    """
    Secured Store Manager
    This class provides secured management of configuration files for
    automated provisioning (e.g. Playground Template, Box Configuration file)
    and DsP-Installer's Operation.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StoreManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, secure_mode=False):
        self._security_mode = secure_mode
        self._security_key = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def init_secure_key(self, salt):
        if self._security_mode:
            self._load_seckey(salt)
        else:
            self._logger.warn("This Repo Manager is working on NON-SECURE Mode")

    def _load_seckey(self, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        p = input("Input the password for secured repository: ")
        self._security_key = base64.urlsafe_b64encode(kdf.derive(p))

    def read_file(self, filename):
        filepath = os.path.join(os.getcwd(), filename)

        file = open(filepath, 'r')
        contents = file.read(-1)
        file.close()

        if self._security_mode:
            self._logger.debug("Enter the read_file with secure mode")
            f = Fernet(self._security_key)
            try:
                contents = f.decrypt(contents)
            except cryptography.fernet.InvalidToken:
                self._logger.error("Password or Salt is not correct.")

        return contents

    def write_file(self, filename, contents):
        filepath = os.path.join(os.getcwd(), filename)

        if self._security_mode:
            f = Fernet(self._security_key)
            contents = f.encrypt(contents)
        file = open(filepath, 'w')
        file.write(contents)
        file.close()


if __name__ == "__main__":
    sr = StoreManager()
    ts = os.urandom(16)
    sr.load_seckey(ts)
