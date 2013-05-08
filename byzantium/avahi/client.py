# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import select
import sys
import os
import pybonjour
import pykka
from ..utils import Utils
from .. import const
from .service_index import ServiceIndex

class AvahiClient(pykka.ThreadingActor):
    def __init__(self, master, timeout=5, regtype='_tcp'):
        ''' listen for avahi traffic with the service type that matches the filters and stick them in the service index'''
        super(AvahiClient,self).__init__()
        self.regtype = regtype
        self.master = master
        self.logging = Utils().get_logging()
        self.timeout = timeout
        self.resolved = []

    def resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname, hosttarget, port, txtRecord):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            self.logging.debug('adding')
            self.master.tell({'record':{'name':fullname,'ipaddr':hosttarget,'port':port, 'service_type':self.record_service_type},'action':'update'})
            self.record_service_type = None
            self.resolved.append(True)

    def browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName, regtype, replyDomain):
        self.record_service_type = regtype
        self.logging.debug(serviceName)
        if errorCode != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            self.master.tell({'record':serviceName+'.'+regtype+replyDomain,'action':'remove'})
            return

        resolve_sdRef = pybonjour.DNSServiceResolve(0, interfaceIndex, serviceName, regtype, replyDomain, self.resolve_callback)

        try:
            while not resolved:
                ready = select.select([resolve_sdRef], [], [], timeout)
                if resolve_sdRef not in ready[0]:
                    self.logging.debug('Resolve timed out',1)
                    break
                pybonjour.DNSServiceProcessResult(resolve_sdRef)
            else:
                self.resolved.pop()
        finally:
            resolve_sdRef.close()
    
    def on_start(self):
        browse_sdRef = pybonjour.DNSServiceBrowse(regtype = self.regtype, callBack = self.browse_callback)
        try:
            try:
                while True:
                    ready = select.select([browse_sdRef], [], [])
                    if browse_sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(browse_sdRef)
            except KeyboardInterrupt:
                pass
        finally:
            browse_sdRef.close()

class AvahiWrangler(pykka.ThreadingActor):
    def on_start(self):
        self.filters = []
        self.service_index = ServiceIndex()
        self.tcp_client = AvahiClient(master=self.actor_ref, regtype='_tcp')
        self.udp_client = AvahiClient(master=self.actor_ref, regtype='_udp')

    def set_filters(self, filters):
        self.filters = filters

    def on_receive(self, message):
        if type(message) == dict:
            if 'record' in message and 'action' in message:
                self.send_filtered(message['record'], message['action'])

    def send_filtered(self, record, action):
        if True in [x.match(record) for i in self.filters]:
                if message['action'] == 'update':
                    self.service_index.update(message['record'])
                elif message['action'] == 'remove':
                    self.service_index.remove(message['record'])

if __name__ == '__main__':
    from .. import const
    from . import filters
    try:
        print('making wrangler')
        client = AvahiWrangler()
        print('setting filters')
        client.set_filters(filters.all)
        print('starting wrangler')
        client.start()
        print('waiting')
    except KeyboardInterrupt:
        sys.exit(1)
