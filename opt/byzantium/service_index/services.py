import web
import re
import logging
from byzantium.view.web.page import Page
from byzantium.config import Config
from byzantium.avahi.service_index import ServiceIndex

# service types (as in dnssd) that can be accessed via a browser or an
#application that can be launched by a browser.
browsable_service_types = ['_http', '_https', '_ftp', '_tftp']

# service index Config object
config = Config('service_index.conf')

# copy of byzantium.const
const = config.const

# copy of an Utils object
utils = config.utils

# new ServiceIndex object
services = ServiceIndex()

# urls to respond to and classes to use to respond
urls = ('/(.*)', 'index')

class index(Page):
	'''
		Renders Service Directory
	'''
	default_input = {'lang':'default', 'type':'any'} # for use when we have multi-lang support
	render = web.template.render(config.get('webpy','templates'), base='layout')	# get templates location from config
	def on_GET(self):
		self.logger.debug(repr(config))
		self.logger.debug(config.get('webpy','templates'))
		self.logger.debug('got GET with web.input: %s' % str(repr(self.web_input)))
		self.set_defaults()
		service_list = self.get_services()	# get a list of dictionaries of service attributes to fill in the templates
		service_sections = []
		for sec in service_list:
			service_sections.append(self.render.service_section(sec=sec))
		if len(service_sections) > 0:
			logging.debug('\n\nFound services\n\n')
			return self.render.services(service_sections)
		else:
			logging.debug('\n\nNo services\n\n')
			return self.render.no_services()

	def get_services(self):
		self.logger.debug('getting services')
		service_list = []
		# test value for service_list # [{'name':'Test', 'url':'http://example.com', 'desc':'testing 1 2 3', 'service':{}}]
		services.pull()
		for name, service in services.get_index().items():
			# name is the dictionary index but is included in the service record as well
			srv = self.get_service(service)
			if srv: service_list.append(srv)
		if not service_list: service_list = []
		return service_list

	def get_service(self, service):
		self.logger.debug('getting a service: %s' % str(service))
		if not service: return None
		name = service['service_name'] or 'unknown'
		url = self.get_service_url(service)
		desc = self.get_service_desc(service)
		if url:
			service_dict = {'name':name, 'url':url, 'desc':desc, 'service':service}
			self.logger.debug('found service: %s' % str(repr(service_dict)) )
			return service_dict
		return None

	def get_service_url(self, service):
		browseable = False
		self.logger.debug('getting the url for a service: %s' % str(service))
		if service['ip_version'] == 6:
			url = '[%s]' % service['ipaddr'].strip().strip('[]')
		else:
			url = service['ipaddr'].strip()
		if service['port'] and service['port'] > 0:
			url = '%s:%s' % (url, str(service['port']))	# append port
		if service['append_to_url']:
			self.logger.error(('service[append_to_url]',service['append_to_url']))
			if service['append_to_url'].startswith('/'):
				url = '%s%s' % (url, service['append_to_url'])
			else:
				url = '%s/%s' % (url, service['append_to_url'])
		for i in browsable_service_types:
			if re.match('^%s' % i,service['service_type']):
				url = '%s://%s' % (i.replace('_',''), url)	# prepend protocol
				browseable = True
				break
		if not browseable:
			url = 'http://%s' % url  # prepend protocol
		self.logger.error('found a url for a service: %s' % str(url))
		return url or ''

	def get_service_desc(self, service):
		self.logger.debug('getting a description for a service: %s' % str(service))
		#FIXME: Add sanitization of description: pre 5.0b
		desc = service['description']
		self.logger.debug('found a description for a service: %s' % str(desc))
		return desc or ''

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
