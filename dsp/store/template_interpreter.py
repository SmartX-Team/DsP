# -*- coding: utf-8 -*-

from dsp.store.store_manager import StoreManager
import logging
import store_exceptions


class TemplateInterpreter:
    # For singleton design
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TemplateInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._store = None
        self._logger = None
        self._boxes = None
        self._template = None
        self._playground = None

    def initialize(self):
        self._store = StoreManager()
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_playground(self):
        self._get_file_instances()
        self._validate_file_format()
        self._playground = self._create_playground()
        return self._playground

    def _get_file_instances(self):
        self._template = self._store.get_template()
        self._boxes = self._store.get_boxes()

    def _validate_file_format(self):
        self._validate_template_format(self._template)
        self._validate_boxes_format(self._boxes)

    # TODO Implement validation for Box.yaml
    def _validate_boxes_format(self, boxes):
        pass

    # TODO Implement validation for playground.yaml
    def _validate_template_format(self, template):
        pass

    def _create_playground(self):
        playground = list()
        try:
            for elem in self._template:
                box = self._find_box_by(elem["same"])
                box.software = elem["software"]
                box.type = elem["Type"]
                playground.append(box)
        except store_exceptions.ElementNotFoundException as exc:
            raise store_exceptions.StoreException(exc.message)
        return playground

    def _find_box_by(self, boxname):
        for box in self._boxes:
            if box.name == boxname:
                return box
        raise store_exceptions.ElementNotFoundException("box.yaml", "hostname", boxname, None)
