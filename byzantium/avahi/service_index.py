# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import os
from collections import Sequence
from ..utils import Utils
from .. import const

class ByzTxt:
    '''
        Class to mangle the txt element of avahi records with certian formatting
    '''
    def __init__(self, txt_record=None):
        self.orig = txt_record
        self.description = None
        self.append_to_url = None
        self.ground_station_address = None # not implemented
        self.pgp = None # not implemented
        self.ns = (const.get('append-string-post-port-key', 'appendtourl'),
                    const.get('service-description-key', 'description'),
                    const.get('groundstation-addr', 'groundstation-addr'),
                    const.get('pgp-pubkey', 'pgp-pubkey'),
                    const.get('pgp-id', 'pgp-id'))
        if self.orig: self.__parse()

    def __parse(self):
        desc_list = []  # accumulator for the multi-line description
        collect_until_next = None  # container to collect lines until another key is found (or EOF).
        for line in self.txt.strip().split('\n'):
            key,val = (line+'=').split('=') # added = on end to prevent it from unpacking to too few items
            val = val.replace('\n', '')
            # if key is a defined key, then make sure collect_until_next is set to None
            if key in self.ns:
(const.get('append-string-post-port-key', 'appendtourl'),
                        const.get('service-description-key', 'description'))
                collect_until_next = None
            if key == const.get('append-string-post-port-key', 'appendtourl'):
                self.append_to_url = val
            elif key == const.get('service-description-key', 'description'):
                desc_list.append(val)
                collect_until_next = [desc_list] # a list so it should be a pointer
            elif key == const.get('groundstation-addr', 'groundstation-addr'):
                self.ground_station_address = val.strip()
            elif key == const.get('pgp-pubkey', 'pgp-pubkey'):
                pass
            elif key == const.get('pgp-id', 'pgp-id'):
                pass
            else:
                if collect_until_next:
                    collect_until_next[0].append(line)
        # reassemble description
        self.description = '\n'.join(desc_list)

class Record:
    def __init__(self, **kwargs):
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
            self.byz_txt = ByzTxt(self.txt)

    def to_dict(self):
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
        return d

    def set_fullname(self):
        ''' set 'fullname' used as a unique id and required by on of the callbacks'''
        if self.name and self.service_type and self.service_domain:
            self.fullname = '%s.%s%s' % (self.name,self.service_type,self.service_domain)

    def from_signal(self, signal, args):
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
            self.byz_txt = ByzTxt(self.txt)
            self.description = self.byz_txt.description
            self.append_to_url = self.byz_txt.append_to_url
        else:
            self.flags = args[5]
        self.set_fullname()

        def byz_txt(self):
            txt = 
            for line in self.txt.strip().split('\n'):
                    key,val = (line+'=').split('=') # added = on end to prevent it from unpacking to too few items
                    # remove newline
                    val = val.replace('\n', '')
                    # if this is 
                    if key == const.get('uri-post-port-string-key', 'appendtourl'):
                        path += val
                    elif key == const.get('service_description_key', 'description'):
                        description += val

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
        self.update(record.to_dict())

    def update(self, record):
        '''merge saved and live copies with preference to the live copy'''
        self._read()
        self._index.add(record.to_dict())
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
