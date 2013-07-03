# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
import logging
import subprocess
from . import convert2type, mknum
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class Utils:
    def __init__(self):
        self.logger = logging
        if 'BYZ_DEBUG' in os.environ and os.environ['BYZ_DEBUG']:
            self.logger.basicConfig(level=logging.DEBUG)
        else:
            self.logger.basicConfig(level=logging.ERROR)

    def __call__(self):
        return self

    def get_logger(self):
        return self.logger

    def get_mesh_ip(self):
        ip = ''
        return ip

    def convert2obj(self, string):
        if string:
            v = string.strip().lower()
            if v is 'true': return True
            elif v is 'true': return True
            elif v is 'false': return False
            elif v in ('none', 'null', ''): return None
        return string

    def ini2list(self, filename):
        '''Load all sections of an ini file as a list of dictionaries'''
        conpar = configparser.SafeConfigParser()
        conpar.read(filename)
        config = []
        for sec in conpar.sections():
            section = {}
            for k,v in conpar.items(sec):
                section[k] = convert2obj(v)
        return config

    def ini2dict(self, filename, section=None):
        '''Load all sections of an ini file as a list of dictionaries'''
        conpar = configparser.SafeConfigParser()
        conpar.read(filename)
        config = {}
        for sec in conpar.sections():
            config[sec] = {}
            for k,v in conpar.items(sec):
                config[sec][k] = convert2type(v)
        if section:
            config = config[section]
        return config

    def dict2ini(self, input_dict, filename):
        '''Load all sections of an ini file as a list of dictionaries'''
        if not filename: raise Exception('No filename passed to dict2ini(data, filename)')
        conpar = configparser.SafeConfigParser()
        config = input_dict
        for sec in config:
            conpar.add_section(str(sec))
            for k,v in config[sec].items():
                conpar.set(str(sec), str(k), str(v))
        with open(filename, 'wb') as inifile:
            conpar.write(inifile)

    def file2str(self, file_name, mode = 'r'):
        if not os.path.exists(file_name):
            self.logger.debug('File not found: '+file_name)
            return ''
        fileobj = open(file_name, mode)
        filestr = fileobj.read()
        fileobj.close()
        return filestr

    def file2json(self, file_name, mode = 'r'):
        filestr = self.file2str(file_name, mode)
        try:
            return_value = json.loads(filestr)
        except ValueError as val_e:
            self.logger.debug(val_e)
            return_value = None
        return return_value

    def str2file(self, string, file_name, mode = 'w'):
        fileobj = open(file_name, mode)
        fileobj.write(string)
        fileobj.close()

    def json2file(self, jsonobj, file_name, mode = 'w'):
        try:
            string = json.dumps(jsonobj)
            self.str2file(string, file_name, mode)
            return True
        except TypeError as type_e:
            self.logger.debug(type_e)
            return False

    def read_cache(self, name):
        return self.file2json(self.const.Const().get('cache', name))

    def write_cache(self, data, name):
        return self.json2file(data, self.const.Const().get('cache', name))
