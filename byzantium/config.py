# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
import glob
from .utils import Utils
from . import const

class Config(object):
    ''' Make me read from a file and/or environment'''
    def __init__(self, config_file=None):
        '''
            @param  config_file     srt, path to config file
                                    either absolute or relative
                                    to the default byzantium config
                                    directory.
        '''
        self.utils = Utils()    # get a Utils object
        self.const = const      # grab const to drag around with you
        self.logger = self.utils.get_logger()
        if config_file and os.path.exists(config_file):    # config file is a full path
            self.config_file = config_file
        elif config_file:   # config file is a partial path or absolute path
            try:
                # attempt to find the config file in the default config dir
                self.config_file = os.path.join(self.const.get('byzantium_dir'), config_file)
            except:
                # i can't find it :(
                self.config_file = 'no file specified'
        else:
            # why no config file ... i can has config file
            self.config_file = 'no file specified'
        self._get_config()  # get config file and load it

    def _get_config_dir(self, dirname, ext='conf'):
        '''
            Load a directory of configs
            @param  dirname     str, directory name. assumed to be under
                                the default config directory unless
                                it is an absolute path.
            @param  ext         str, file extention of files to load.
                                defaults to 'conf' (do not include leading '.')
        '''
        confs = []
        self.logger.debug('_get_config_dir', dirname, ext)
        if not os.path.isdir(dirname):
            byz_dir = self.const.get('byzantium_dir')
            dirname = os.path.join(byz_dir, dirname)
        self.logger.debug(dirname+'/*.'+ext)
        for f in glob.glob(dirname+'/*.'+ext):
            self.logger.debug('ext config path: %s' % f)
            conf = Config(path=f)
            confs.append(conf)
            del conf
        return confs

    def _get_config(self):
        '''load individual config file'''
        if os.path.exists(self.config_file):
            self._values = self.utils.ini2dict(self.config_file, 'main')
            self.logger.debug(self._values)
        else:
            self._values = {}

    def __call__(self):
        return self._values

    def _set_type(self, value, default, _type):
        '''
            Set value type
            @param  value   config value
            @param  default default to return if not successful
            @param  _type   type to set to via _type(value)
        '''
        self.logger.debug('_set_type', value, default, _type)
        if _type == 'config_dir':
            self.logger.debug('_set_type: config_dir', value)
            confs = self._get_config_dir(value)
            self.logger.debug('found', confs)
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
        '''
            get a value from the config object
            @param  default     str default value (defaults to None)
            @param  set_type    str set type of config
            @param  keys        *str config items and/or sections
            call with config strings in sections->items then kwargs
        '''
        default = set_type = None
        if 'default' in kwargs: default = kwargs['default']
        if 'set_type' in kwargs: set_type = kwargs['set_type']
        if set_type in ('config_dir', 'config'):
            self.logger.debug('shortcircuit: config typ specified')
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
        '''
            Get an item from the config via self.get()
            @param  key     config item name
        '''
        return self.get(key)

    def reload(self):
        '''reload config from the source file'''
        self._get_config()
