# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
from ..utils import Utils
from .. import const

class ServiceIndex:
    def __init__(self):
        self.__file = const.get('service-index')
        self.utils = Utils()
        self._index_dict = {}

    def _write(self):
        self.utils.dict2ini(self._index_dict, self.__file)

    def _read(self):
        if os.path.exists(self.__file):
            self._index_dict = self.utils.ini2dict(self.__file)

    def _wipe(self):
        pass

    def add(self, record):
        self.update(record)

    def update(self, record):
        self._read()
        self.index_dict.update(record)
        self._write()

    def remove(self, key):
        self._read()
        if key in self.index_dict:
            del self.index_dict[key]
        self._write()
