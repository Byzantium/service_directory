# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

from byzantium.avahi.filter import AvahiFilter

class Filter(AvahiFilter):
    '''Dummy service types filter'''
    def match(self, record, action=None):
        '''match nothing'''
        print('dummy_filter.match()')
        return False
