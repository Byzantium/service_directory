# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
import sys
import logging
import subprocess
from . import convert_to_type, convert_from_type, mknum
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class Utils:
    def __init__(self):
        self.logger = logging.getLogger('python-byzantium')
        if 'BYZ_DEBUG' in os.environ and os.environ['BYZ_DEBUG']:
            self.log_level = logging.DEBUG
        else:
            self.log_level = logging.ERROR
        self.__set_file_logging(self.logger, '/tmp/byantium.log', self.log_level)#const.get('global-log-file'), self.log_level)
        self.__set_stderr_logging(self.logger, self.log_level)
        self.logger.debug('Utils.__init__')

    def __call__(self):
        self.logger.debug('called utils')
        return self

    def __set_file_logging(self, logger, filename, level):
        log_file_handler = logging.FileHandler(filename)
        log_file_handler.setLevel(level)
        logger.addHandler(log_file_handler)

    def __set_stderr_logging(self, logger, level):
        log_stream_handler = logging.StreamHandler(sys.stderr)
        log_stream_handler.setLevel(level)
        logger.addHandler(log_stream_handler)

    def get_logger(self, name=None, level=None, filename=None, new=False):
        self.logger.debug('got logger')
        if not new: return self.logger
        if name:
            logger = logging.getLogger(name)
        else:
            logger = logging.getLogger()
        if not level: level = self.log_level
        logger.setLevel(level)
        if filename: self.__set_file_logging(logger, filename, level)
        return logger

    def get_mesh_ip(self):
        ip = ''
        return ip

    def ini2list(self, filename, convert=False):
        '''Load all sections of an ini file as a list of dictionaries'''
        conpar = configparser.SafeConfigParser()
        conpar.read(filename)
        config = []
        for sec in conpar.sections():
            section = {}
            for k,v in conpar.items(sec):
                section[k] = convert_to_type(v, convert)
        return config

    def ini2dict(self, filename, section=None, convert=False):
        '''Load all sections of an ini file as a list of dictionaries'''
        conpar = configparser.SafeConfigParser()
        conpar.read(filename)
        config = {}
        logging.debug('sections %s' % repr(conpar.sections()))
        for sec in conpar.sections():
            logging.debug('sec, conpar.items(sec): %s\n%s' % (sec, repr(conpar.items(sec))))
            config[sec] = {}
            for k,v in conpar.items(sec):
                logging.debug('for k, v in conpar.items(sec): k, v: %s, %s' % (k, v))
                config[sec][k] = convert_to_type(v, convert)
        if section:
            config.update(config[section])
            logging.debug('config.__call__: %s' % repr(config))
        return config

    def dict2ini(self, input_dict, filename, convert=False):
        '''Load all sections of an ini file as a list of dictionaries'''
        if not filename: raise Exception('No filename passed to dict2ini(data, filename)')
        conpar = configparser.SafeConfigParser()
        config = input_dict
        for sec in config:
            conpar.add_section(str(sec))
            for k,v in config[sec].items():
                conpar.set(str(sec), str(k), convert_from_type(v, convert))
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
