# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
import glob
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

    def _get_config_dir(self, dirname, ext='conf'):
        confs = []
        print('_get_config_dir',dirname, ext)
        if not os.path.isdir(dirname):
            byz_dir = self.const.get('byzantium_dir')
            dirname = os.path.join(byz_dir, dirname)
        print(dirname+'/*.'+ext)
        for f in glob.glob(dirname+'/*.'+ext):
            print('ext config path: %s' % f)
            conf = Config(path=f)
            confs.append(conf)
            del conf
        return confs

    def _get_config(self):
        if os.path.exists(self.config_file):
            self._values = self.utils.ini2dict(self.config_file, 'main')
            print(self._values)
        else:
            self._values = {}

    def __call__(self):
        return self._values

    def _set_type(self, value, default, _type):
        print('_set_type',value, default, _type)
        if _type == 'config_dir':
            print('_set_type: config_dir', value)
            confs = self._get_config_dir(value)
            print('found', confs)
            return confs
        elif not _type or type(value) == _type:
            return value
        else:
            try:
                return _type(value)
            except TypeError as e:
                logging.error(e)
        return default

    def get(self, *keys, **kwargs):
        default = set_type = None
        if 'default' in kwargs: default = kwargs['default']
        if 'set_type' in kwargs: set_type = kwargs['set_type']
        if set_type in ('config_dir','config'):
            print('shortcircuit: config typ specified')
            return self._set_type(keys[0], default, set_type)
        if len(keys) > 1:
            values = self._values.copy()
            for k in keys:
                if k in values:
                    values = values[k]
            return self._set_type(values, default, set_type)
        elif len(keys) == 1:
            key = keys[0]
            if key in self._values:
                return self._set_type(self._values[key], default, set_type)
        return default

    def __getitem__(self, key):
        return self.get(key)

    def reload(self):
        self._get_config()
