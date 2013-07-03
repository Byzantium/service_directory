import web

__license__ = 'GPL v3'

__author__ = 'haxwithaxe me@haxwithaxe.net'

'''
Utilities for Project Byzantium to use with Web.py
'''

class Page:
	'''
		web page abstract class
	'''
	default_inputs = {}
	web_input = None	# class wide access to current web.input()
	render = None	# class wide access to the template engine
	def GET(self, *args):
		self.web_input = web.input()
		self.on_GET()
	
	def set_defaults(self):
		defaluts = self.default_input.copy()	# avoid overwriting default_input
		# merge giving preference to web_input
		defaults.update(web_input)
		self.web_input = defaults

	def on_GET(self):
		self.set_defaults
		if self.render:
			self.render.index(self.web_input)
		else:
			return 'Hello world!'

class Form(Page):
	'''
		Form class template.
		Extends Page with POST and on_POST.
	'''
	def POST(self, *args):
		self.web_input = web.input()
		self.on_POST()
	def on_POST(self):
		self.set_defaults
		if self.render:
			return self.render.index(self.web_input)
		else:
			return 'Hello world!'



