import web
from .byzweb import Page
from ..config import Config
from ..avahi.service_index import ServiceIndex

browsable_service_types = ['_http', '_https', '_ftp', '_tftp']

config = Config('service-index.conf')
const = config.const
utils = config.utils
logger = utils.get_logger()
services = ServiceIndex()

urls = {'/services(.*)':'index'}

class index(Page):
	'''
		Renders Service Directory
	'''
	default_input = {'lang':'default', 'type':'any'}
	render = web.template.render(config.get('webpy','templates'))	# get templates location from config
	def on_GET(self):
		logger.debug('got GET with web.input: %s' % str(repr(web_input)))
		self.set_defaults()
		service_list = self.get_services()	# get a list of dictionaries of service attributes to fill in the templates
		service_sections = []
		for sec in service_list:
			service_sections.append(render.service_section(sec))
		if len(service_sections) > 0:
			return render.services(''.join(service_sections))
		else:
			return render.no_services()

	def get_services(self):
		service_list = []
		for s in services:
			srv = self.get_service(s)
			if srv: service_list.append(srv)

	def get_service(self, service):
		name = service.service_name or 'unknown'
		url = self.get_service_url(service)
		desc = self.get_service_desc(service)
		if url:
			return {'name':name, 'url'=url, 'desc'=desc, 'service':service.to_dict()}
		return None

	def get_service_url(self, service):
		if service.ip_version == 6:
			url = '[%s]' % service.ipaddr.strip().strip('[]')
		else:
			url = service.ipaddr.strip()
		if service.port and service.port > 0:
			url = ':'.join(url, str(service.port))	# append port
		if service.append_to_url:
			url = url+service.append_to_url
		for i in browsable_service_types:
			if service.service_type.contains(i):
				url = '://'.join(i.replace('_',''), url)	# prepend protocol
				break
		return url or ''

	def get_service_desc(self, service):
		#FIXME: Add sanitization of description: pre 5.0b
		desc = service.description
		return desc or ''

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()
