# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

import sys
import os
import time
import pykka
import dbus, gobject, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
from ..utils import Utils
from .. import const
from .service_index import ServiceIndex

def envent_to_record(mode,*args):
    '''
    ItemNew/ItemRemove:
        out int interface
        out int protocol
        out string name
        out string stype
        out string domain
        out u flags
    Failure:
        string error
    '''
    record = None
    if mode in ('ItemNew','ItemRemove'):
        interface = args[0]
        protocol = args[1]
        name = args[2]
        stype = args[3]
        domain = args[4]
        flags = args[5]
        ipaddr = None
        fullname = name+'.'+stype+domain
        record = {'name':fullname,
                'ipaddr':ipaddr,
                'port':port,
                'service_type':stype,
                'interface':interface,
                'protocol':protocol,
                'service_name':name,
                'service_type':type,
                'domain':domain,
                'flags':flags
                }
    elif mode == 'Failure':
        record = {'error':args[0]}
    return record

class AvahiClient(pykka.ThreadingActor):
    def __init__(self, master, service_type='_tcp', domain=None):
        '''
            listen for avahi traffic matching service_type and pass them on to the AvahiWrangler.
            see avahi API docs here:
                http://avahi.org/download/doxygen/lookup_8h.html#a52d55a5156a7943012d03e6700880d2b ('type' and 'domain')
            see registered service types here: http://www.dns-sd.org/ServiceTypes.html
            Project Byzantium uses __byz__._tcp (even when the protocol is udp).
            service_type must at minimum contain either '_tcp' or '_udp'.
            - in their infinite wisdom the people who make the API can't fathom anyone wanting both at once
                so it has to be one or the other :P
        '''
        super(AvahiClient,self).__init__()
        self.service_type = service_type
        self.domain = domain or u'local'
        self.master = master
        self.logger = Utils().get_logger()

    def add_record(self, *args):
        srvc = args2record(*args)
        print('adding')
        self.logger.debug('adding')
        self.master.tell({'record':srvc,'action':'update'})

    def remove_record(self, *args):
        srvc = args2record(*args)
        print('removing')
        self.master.tell({'record':srvc,'action':'remove'})

    def handle_new(self, *args):
        srvc = args2record(*args)
        self.logger.trace('Found service \'%s\' type \'%s\' domain \'%s\' ' % (srvc['service_name'], srvc['service_type'], srvc['domain']))
        if flags & avahi.LOOKUP_RESULT_LOCAL:
            self.logger.trace('Found service \'%s\' type \'%s\' is local ' % (srvc['name'], srvc['service_type']))
            pass
        self.server.ResolveService(srvc['interface'], srvc['protocol'], srvc['service_name'], srvc['service_type'],
                            srvc['domain'], avahi.PROTO_UNSPEC, dbus.UInt32(0),
                            reply_handler=self.add_record, error_handler=self.handle_avahi_error)

    def handle_dead(self, *args):
        srvc = args2record(*args)
        self.logger.trace('Removing service \'%s\' type \'%s\' domain \'%s\' ' % (srvc['service_name'], srvc['service_type'], srvc['domain']))
        if flags & avahi.LOOKUP_RESULT_LOCAL:
            self.logger.trace('Local service \'%s\' type \'%s\' is local ' % (srvc['name'], srvc['service_type']))
            pass
        self.server.ResolveService(srvc['interface'], srvc['protocol'], srvc['service_name'], srvc['service_type'],
                            srvc['domain'], avahi.PROTO_UNSPEC, dbus.UInt32(0),
                            reply_handler=self.remove_record, error_handler=self.handle_avahi_error)

    def handle_avahi_error(self, *args):
        self.logger.error('Error: %s: %s\n\t%s' % (__name__, str(repr(args[0]))))

    def on_receive(self, message):
        self.logger.debug('client: got message: %s' % str(repr(message)))

    def on_stop(self):
        print('AvahiClient.on_stop()')

    def on_start(self):
        print('AvahiClient.on_start()')
        self.loop = DBusGMainLoop()
        self.bus = dbus.SystemBus(mainloop=self.loop)
        self.server = dbus.Interface( self.bus.get_object(avahi.DBUS_NAME, '/'),
                                'org.freedesktop.Avahi.Server')
        self.sbrowser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME,
                                self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                avahi.PROTO_UNSPEC, self.service_type, self.domain, dbus.UInt32(0))),
                                avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        self.sbrowser.connect_to_signal('ItemNew', self.handle_new)
        #self.sbrowser.connect_to_signal('ItemRemove', self.handle_dead)
        gobject.MainLoop().run()


class AvahiWrangler(pykka.ThreadingActor):
    def __init__(self, filters=[], domain=None, search_service_types=[]):
        super(AvahiWrangler, self).__init__()
        self.filters = filters
        self.domain = domain
        self.search_service_types = search_service_types

    def on_start(self):
        print('AvahiWrangler.on_start()')
        self.service_index = ServiceIndex()
        self.clients = []
        for sst in self.search_service_types:
            client = AvahiClient.start(master=self.actor_ref, service_type=sst,domain=self.domain)
            self.clients.append(client)

    def on_receive(self, message):
        print('got message: %s' % str(repr(message)))
        if type(message) == dict:
            if 'record' in message and 'action' in message:
                self.send_filtered(message['record'], message['action'])

    def send_filtered(self, record, action):
        print('got record: %s, %s' % (record, action))
        if True in [x.match(record, action) for i in self.filters]:
            if message['action'] == 'update':
                self.service_index.update(message['record'])
            elif message['action'] == 'remove':
                self.service_index.remove(message['record'])

    def on_stop(self):
        [x.stop() for x in self.clients]

if __name__ == '__main__':
    from .. import const
    from . import filters

    domain = None # None for default behavior
    search_service_types = [u'_tcp'] # , u'_udp']

    try:
        print('starting wrangler')
        client = AvahiWrangler.start(filters=filters, domain=domain, search_service_types=search_service_types)
        print('waiting')
    except KeyboardInterrupt:
        print('keyboard interupt __main__')
        client.stop()
        sys.exit(1)
