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
from .service_index import ServiceIndex,Record

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
        self.logger = Utils().get_logger(new=True)

    def add_record(self, *args):
        srvc = Record()
        srvc.from_signal('Found',*args)
        self.logger.debug('adding')
        self.master.tell({'record':srvc,'action':'update'})

    def remove_record(self, *args):
        srvc = Record()
        srvc.from_signal('ItemRemove', *args)
        self.logger.debug('removing')
        self.master.tell({'record':srvc,'action':'remove'})

    def handle_new(self, *args):
        srvc = Record()
        srvc.from_signal('ItemNew',*args)
        self.logger.trace('Found service \'%s\' type \'%s\' domain \'%s\' ' % (srvc.service_name, srvc.service_type, srvc.service_domain))
        if srvc.flags & avahi.LOOKUP_RESULT_LOCAL:
            self.logger.trace('Found service \'%s\' type \'%s\' is local ' % (srvc.service_name, srvc.service_type))
            pass
        self.server.ResolveService(srvc.interface, srvc.protocol, srvc.service_name, srvc.service_type,
                            srvc.service_domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
                            reply_handler=self.add_record, error_handler=self.handle_avahi_error)

    def handle_dead(self, *args):
        srvc =  Record()
        srvc.from_signal('ItemRemove',*args)
        self.logger.trace('Removing service \'%s\' type \'%s\' domain \'%s\' ' % (srvc.service_name, srvc.service_type, srvc.service_domain))
        if srvc.flags & avahi.LOOKUP_RESULT_LOCAL:
            self.logger.trace('Local service \'%s\' type \'%s\' is local ' % (srvc.service_name, srvc.service_type))
            pass
        self.server.ResolveService(srvc.interface, srvc.protocol, srvc.service_name, srvc.service_type,
                            srvc.service_domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
                            reply_handler=self.remove_record, error_handler=self.handle_avahi_error)

    def handle_avahi_error(self, *args):
        self.logger.error('Error: %s: %s\n\t%s' % (__name__, str(repr(args[0]))))

    def on_receive(self, message):
        self.logger.debug('client: got message: %s' % str(repr(message)))

    def on_stop(self):
        self.logger.debug('AvahiClient.on_stop()')

    def on_start(self):
        self.logger.debug('AvahiClient.on_start()')
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
        self.logger = Utils().get_logger(name='AvahiWrangler', new=True)
        self.logger.debug('AvahiWrangler.__init__')
        super(AvahiWrangler, self).__init__()
        self.filters = filters
        self.domain = domain
        self.search_service_types = search_service_types

    def on_start(self):
        self.logger.debug('AvahiWrangler.on_start()')
        self.service_index = ServiceIndex()
        self.clients = []
        for sst in self.search_service_types:
            client = AvahiClient.start(master=self.actor_ref, service_type=sst,domain=self.domain)
            self.clients.append(client)

    def on_receive(self, message):
        self.logger.debug('got message: %s' % str(repr(message)))
        if type(message) == dict:
            if 'record' in message and 'action' in message:
                self.send_filtered(message['record'], message['action'])

    def send_filtered(self, record, action):
        self.logger.debug('AvahiWrangler.send_filtered')
        self.logger.debug('got record: %s, %s' % (record, action))
        if True in [x.match(record, action) for i in self.filters]:
            if message['action'] == 'update':
                self.service_index.update(message['record'])
            elif message['action'] == 'remove':
                self.service_index.remove(message['record'])

    def on_stop(self):
        self.logger.debug('AvahiWrangler.on_stop')
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
