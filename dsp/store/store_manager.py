# -*- coding: utf-8 -*-
import os
import yaml
import base64
import logging

import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


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

    def get_template(self):
        filename = "playground.yaml"
        template = self._load_yaml_instance_from_text(self.read_file(filename))
        return template

    def get_boxes(self):
        filename = "box.yaml"
        boxes = self._load_yaml_instance_from_text(self.read_file(filename))
        return boxes

    def init_secure_key(self, salt):
        if self._security_mode:
            self._load_seckey(salt)
        else:
            self._logger.warning("This Repo Manager is working on NON-SECURE Mode")

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
        filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

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

    def _load_yaml_instance_from_text(self, _yaml_text):
        # Parse the data from YAML template.
        try:
            self._logger.info("Parse YAML from the file: \n" + _yaml_text)
            return yaml.load(_yaml_text, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                self._logger.error(("YAML Format Error: In the give YAML text, (Position: line %s, column %s)" %
                                    (mark.line + 1, mark.column + 1)))
                raise yaml.YAMLError(exc)


if __name__ == "__main__":
    sr = StoreManager()
    print(sr.get_boxes())
    print(sr.get_template())
