# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
from collections import Sequence
from ..utils import Utils
from ..config import Config
from .. import const

logger = Utils().get_logger(name='ServiceIndex', new=True)

class ByzTxt:
    '''
        Class to mangle the txt element of avahi records with certian formatting
    '''
    def __init__(self, txt_record=None, config=None):
        logger.debug('ByzTxt.__init__')
        self.config = config
        self.orig = txt_record
        self.description = None
        self.append_to_url = None
        self.ground_station_address = None # not implemented
        self.pgp = None # not implemented
        self.ns = (self.config.get('append-string-post-port-key', 'appendtourl'),
                    self.config.get('service-description-key', 'description'),
                    self.config.get('groundstation-addr', 'groundstation-addr'),
                    self.config.get('pgp-pubkey', 'pgp-pubkey'),
                    self.config.get('pgp-id', 'pgp-id'))
        if self.orig: self.__parse()

    def __parse(self):
        logger.debug('ByzTxt.__parse')
        desc_list = []  # accumulator for the multi-line description
        collect_until_next = None  # container to collect lines until another key is found (or EOF).
        for line in self.txt.strip().split('\n'):
            key,val = (line+'=').split('=') # added = on end to prevent it from unpacking to too few items
            val = val.replace('\n', '')
            # if key is a defined key, then make sure collect_until_next is set to None
            if key in self.ns:
                collect_until_next = None
            if key == self.config.get('append-string-post-port-key', 'appendtourl'):
                self.append_to_url = val
            elif key == self.config.get('service-description-key', 'description'):
                desc_list.append(val)
                collect_until_next = [desc_list] # a list so it should be a pointer
            elif key == self.config.get('groundstation-addr', 'groundstation-addr'):
                self.ground_station_address = val.strip()
            elif key == self.config.get('pgp-pubkey', 'pgp-pubkey'):
                pass
            elif key == self.config.get('pgp-id', 'pgp-id'):
                pass
            else:
                if collect_until_next:
                    collect_until_next[0].append(line)
        # reassemble description
        self.description = '\n'.join(desc_list)

class Record:
    def __init__(self, **kwargs):
        logger.debug('Record.__init__')
        self.config = kwargs.get('config')
        self.fullname = None
        self.interface = kwargs.get('interface')
        self.protocol = kwargs.get('protocol')
        self.service_name = kwargs.get('service_name')
        self.service_type = kwargs.get('service_type')
        self.service_domain = kwargs.get('service_domain')
        self.hostname = kwargs.get('hostname')
        self.ip_version = kwargs.get('ip_version')
        self.ipaddr = kwargs.get('ipaddr')
        self.port = kwargs.get('port')
        self.txt = kwargs.get('txt')
        self.flags = kwargs.get('flags')
        self.description = None
        self.append_to_url = None
        self.set_fullname()
        self.byz_txt = None
        if self.txt:
            self.byz_txt = ByzTxt(self.txt, self.config)

    def to_dict(self):
        logger.debug('Record.to_dict')
        d = {}
        d['fullname'] = self.fullname
        d['interface'] = self.interface
        d['protocol'] = self.protocol
        d['service_name'] = self.service_name
        d['service_type'] = self.service_type
        d['service_domain'] = self.service_domain
        d['hostname'] = self.hostname
        d['ip_version'] = self.ip_version
        d['ipaddr'] = self.ipaddr
        d['port'] = self.port
        d['txt'] = self.txt
        d['flags'] = self.flags
        d['append_to_url'] = self.append_to_url
        d['description'] = self.description
        logger.debug('Record.to_dict: %s' % str(repr(d)) )
        return d

    def set_fullname(self):
        ''' set 'fullname' used as a unique id and required by on of the callbacks'''
        logger.debug('Record.set_fullname')
        if self.name and self.service_type and self.service_domain:
            self.fullname = '%s.%s%s' % (self.name,self.service_type,self.service_domain)
            logger.debug('Record.set_fullname: %s' % self.fullname)

    def from_signal(self, signal, args):
        logger.debug('Record.from_signal')
        argc = len(args)
        if signal in ('ItemNew','ItemRemove', 'Found'):
            self.interface = args[0]
            self.protocol = args[1]
            self.name = args[2]
            self.service_type = args[3]
            self.service_domain = args[4]
            # If this is called from a ResolveService callback
            #set the extra bits it has that we just set to None.
            if signal == 'Found':
                self.hostname = args[5]
                self.ip_version = args[6]
                self.ipaddr = args[7]
                self.port = args[8]
                self.txt = args[9]
                self.flags = args[10]
                self.byz_txt = ByzTxt(self.txt, self.config)
                self.description = self.byz_txt.description
                self.append_to_url = self.byz_txt.append_to_url
            else:
                self.flags = args[5]
        self.set_fullname()


class ServiceIndex:
    def __init__(self):
        logger.debug('ServiceIndex.__init__')
        self.config = Config('service_index.conf')
        self.__file = self.config.get('service-index')
        self.utils = Utils()
        self._index = {}

    def dump(self):
        logger.debug('ServiceIndex.dump')
        logger.debug(repr(self._index))
        return self._index

    def get_index(self):
        return self._index

    def _write(self):
        logger.debug('ServiceIndex._write')
        self.utils.dict2ini(self._index, self.__file)

    def _read(self):
        logger.debug('ServiceIndex._read')
        if self.__file and os.path.exists(self.__file):
            self._index = self.utils.ini2dict(self.__file)

    def _wipe(self):
        '''clear saved and live copies.'''
        logger.debug('ServiceIndex._wipe')
        self._index = {}
        self._write()

    def add(self, record):
        '''
            add item to the saved copy
            same as update.
        '''
        logger.debug('ServiceIndex.add')
        self.update(record)

    def update(self, record):
        '''merge saved and live copies with preference to the live copy'''
        logger.debug('ServiceIndex.update')
        self._read()
        self._index.update({record.fullname:record.to_dict()})
        self._write()

    def pull(self):
        ''' dump live copy and read the saved one'''
        logger.debug('ServiceIndex.pull')
        self._index = {}
        self._read()

    def push(self):
        ''' write the live copy overwriting the saved one'''
        logger.debug('ServiceIndex.push')
        self._write()

    def remove(self, key):
        '''remove item from the save copy'''
        logger.debug('ServiceIndex.remove')
        self._read()
        if key in self._index:
            del self._index[key]
        self._write()
