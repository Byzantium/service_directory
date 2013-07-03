# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
from collections import Sequence
from ..utils import Utils
from .. import const

class Index:
    def __init__(self):
        self.data = {}
        self.data_iter = []

    def __call__(self, values=None):
        return self.data

    def __getitem__(self, key):
        return self.data[key]

    def iterrable(self):
        return self.data_iter

    def __reset_iter(self):
        self.data_iter = [(x,y) for x,y in self.data.items()]

    def set(self, values):
        self.data = values
        self.__reset_iter()

    def add(self,value):
        self.data.update(value)
        self.__reset_iter()

    def drop(self,key):
        del self.data[key]
        self.__reset_iter()

    def pop(self):
        return self.data_iter.pop()


class ServiceIndex(Sequence):
    def __init__(self):
        self.__file = const.get('service-index')
        self.utils = Utils()
        self._index = Index()

    def __getitem__(self, key):
        return self._index[key]

    def __len__(self):
        return len(self._index.iterrator())

    def dump(self):
        print(repr(self._index.data))
        return self._index

    def next(self):
        if not self._index.iterable():
            raise StopIteration
        return self._index.pop()

    def _write(self):
        self.utils.dict2ini(self._index.data, self.__file)

    def _read(self):
        if self.__file and os.path.exists(self.__file):
            self._index.set(self.utils.ini2dict(self.__file))

    def _wipe(self):
        '''clear saved and live copies.'''
        self.__index.set({})
        self._write()

    def add(self, record):
        '''
            add item to the saved copy
            same as update.
        '''
        self.update(record)

    def update(self, record):
        '''merge saved and live copies with preference to the live copy'''
        self._read()
        self._index.add(record)
        self._write()

    def pull(self):
        ''' dump live copy and read the saved one'''
        self._index.set({})
        self._read()

    def push(self):
        ''' write the live copy overwriting the saved one'''
        self._write()

    def remove(self, key):
        '''remove item from the save copy'''
        self._read()
        if key in self._index.data:
            self._index.drop(key)
        self._write()
