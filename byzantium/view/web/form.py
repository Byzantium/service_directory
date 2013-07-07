import web
from ...utils import Utils

__license__ = 'GPL v3'

__author__ = 'haxwithaxe me@haxwithaxe.net'

'''
Utilities for Project Byzantium to use with Web.py
Form prototype
'''

class Form(Page):
	'''
		Form class template.
		Extends Page with POST and on_POST.
	'''
	def POST(self, *args):
		self.logger.debug('got POST')
		self.web_input = web.input()
		self.logger.debug('got web.input: %s' % str(repr(self.web_input)) )
		return self.on_POST()

	def on_POST(self):
		''' example /placeholder '''
		self.set_defaults
		if self.render:
			return self.render.index(self.web_input)
		else:
			return 'Hello world!'



