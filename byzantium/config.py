# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
from .utils import Utils
from . import const

class Config(object):
    ''' Make me read from a file and/or environment'''
    def __init__(self, config_file=None, path=None):
        self.utils = Utils()
        self.const = const
        if path:
            self.config_file = path
        elif config_file:
            try:
                self.config_file = os.path.join(self.const.get('byzantium_dir'), config_file)
            except:
                self.config_file = 'no file specified'
        else:
            self.config_file = 'no file specified'
        self._get_config()

    def _get_config(self):
        if os.path.exists(self.config_file):
            self._values = ini2dict(self.config_file)
        else:
            self._values = {}

    def __call__(self):
        return self._values

    def get(self, key, default=None):
        if key in self._values:
            return self._values[key]
        return default

    def __getitem__(self, key):
        return self.get(key)

    def reload(self):
        self._get_config()
