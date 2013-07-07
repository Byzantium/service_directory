import web
from ...utils import Utils

__license__ = 'GPL v3'

__author__ = 'haxwithaxe me@haxwithaxe.net'

'''
Utilities for Project Byzantium to use with Web.py
'''

class Page:
	'''
		web page abstract class
	'''
	utils = Utils()
	logger_name = 'Page'
	logger = utils.get_logger(name=logger_name, new=True)
	default_inputs = {}
	web_input = None	# class wide access to current web.input()
	render = None	# class wide access to the template engine
	path = ()
	def GET(self, *args):
		self.logger.debug('got GET')
		self.logger.debug('got args: %s' % str(repr(args)))
		self.web_input = web.input()
		self.logger.debug('got web.input: %s' % str(repr(self.web_input)) )
		return self.on_GET()
	
	def set_defaults(self):
		self.logger.debug('setting default web.input')
		defaults = self.default_input.copy()	# avoid overwriting default_input
		# merge giving preference to web_input
		defaults.update(self.web_input)
		self.web_input = defaults

	def on_GET(self):
		''' example /placeholder '''
		self.set_defaults
		if self.render:
			self.render.index(self.web_input)
		else:
			return 'Hello world!'

