import web
import re
import sys
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
utils.write_pid(sys.argv[0])

# new ServiceIndex object
services = ServiceIndex()

# urls to respond to and classes to use to respond
urls = ('/(.*)', 'index')

SHOW_TO_HUMANS = ('user')
SHOW_DEBUG = ('debug')

class index(Page):
	'''
		Renders Service Directory
	'''
	default_input = {'show':'user', 'lang':'default', 'type':'any'} # for use when we have multi-lang support
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

	def filter_records(self, records):
		filter_by = self.web_input['filterby'] or '*'
		filter_word = self.web_input['filter'] or '*'
		records = [ (not self.filter_record(filter_by, filter_word, x) or x) for x in records ]
		return records

	def filter_record(self, filter_by, filter_word, record):
		if not filter_word:
			return False
		if type(filter_by) == list:
			for key, value in record.items():
				if key in filter_by and value.contains(filter_word):
					return True
		elif filter_by in record:
			return str(record[filter_by]).contains(filter_word)
		elif filter_by == '*':
			for r in record.values():
				if r.contains(filter_word):
					return True
		return False

	def sort_records(self, records):
		sort_by = self.web_input['sortby'] or 'name'
		sort_direction = self.web_input['sortdir'] or ASCENDING
		sorted(records, key=lambda r: r[sort_by])
		if sort_direction == DESCENDING:
			records.reverse()
		return records

	def get_services(self):
		self.logger.debug('getting services')
		service_list = []
		# test value for service_list # [{'name':'Test', 'url':'http://example.com', 'desc':'testing 1 2 3', 'service':{}}]
		services.pull()
		attribs = {'show':self.web_input['show']}
		service_list = self.filter_records(service_list)
		for name, service in services.get(**attribs).items():
			# name is the dictionary index but is included in the service record as well
			srv = self.get_service(service)
			if srv:
				service_list.append(srv)
		service_list = self.sort_records(service_list)
		return service_list

	def get_service(self, service):
		self.logger.debug('getting a service: %s' % str(service))
		if not service:
			return None
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
			self.logger.debug(('service[append_to_url]',service['append_to_url']))
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
		self.logger.debug('found a url for a service: %s' % str(url))
		return url or ''

	def get_service_desc(self, service):
		self.logger.debug('getting a description for a service: %s' % str(service))
		#FIXME: Add sanitization of description: asap
		desc = service['description']
		self.logger.debug('found a description for a service: %s' % str(desc))
		return desc or ''

if __name__ == "__main__":
	app = web.application(urls, globals())
	byzantium
	app.run()
	utils.remove_pid(sys.argv[0])
