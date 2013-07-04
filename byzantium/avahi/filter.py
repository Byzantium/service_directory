# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

from .. import utils

class AvahiFilter:
    def __init__(self):
        self.logger = utils.Utils().get_logger()

    def match(self, record, action=None):
        '''
            Do something with the Record passed with a new service, new info about a service or a removed one.
            return True to have the Record stored in the service index
            return false to let other filters decide
        '''
        return False
