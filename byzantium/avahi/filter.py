# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

from .. import utils

class AvahiFilter:
    def __init__(self):
        self.logging = utils.Utils().get_logging()

    def match(self, record):
        '''
        do something with the record passed with a new service, new info about a service or a removed one.
        return True to have the record stored in the service index
        return false to let other filters decide
        '''
        return False
