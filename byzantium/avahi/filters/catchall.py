# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

from ..filter import AvahiFilter
import re

class Filter(AvahiFilter):
    byz_tcp = re.compile('[\w.-]*__byz__\._tcp')
    byz_udp = re.compile('[\w.-]*__byz__\._udp')
    def match(self, record):
        '''match every record for a byzantium service'''
        if byz_tcp.match(record['service_type']) or byz_tcp.match(record['service_type']):
            return True
        else:
            return False
