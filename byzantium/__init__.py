# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

BYZANTIUM_CONSTANTS = '/opt/byzantium/byzantium_const.conf'

class Const:
    def __init__(self):
        self.config = {}
        self.load()

    def __call__(self):
        return self.config

    def get(self, *keys, **kwargs):
        if 'default' in kwargs:
            default = kwargs['default']
        else:
            default = None
        item = None
        depth = len(keys)
        if depth > 1:
            for i in range(0,depth-1):
                if keys[i] in self.config:
                    if i is 0:
                        item = self.config[keys[i]]
                    else:
                        item = item[keys[i]]
                else:
                    return item
        else:
            if keys[0] in self.config:
                return self.config[keys[0]]
        return default_value

    def load(self):
        '''Load all sections of an ini file as a list of dictionaries'''
        conpar = configparser.SafeConfigParser()
        conpar.read(BYZANTIUM_CONSTANTS)
        self.config = {}
        for sec in conpar.sections():
            if sec == 'main':
                for k,v in conpar.items(sec):
                    self.config[k] = convert2obj(v)
            else:
                self.config[sec] = {}
                for k,v in conpar.items(sec):
                    self.config[sec][k] = convert2obj(v)
        return self.config

const = Const().load()

__all__ = ['avahi','const', 'config', 'utils']
