

#originally: delegate.py via http://webpy.org/multiple_apps
import web

class Site(web.application):
   '''
      Delegates appropriate app based on prefix.
      `pages` should be a list of (byzantium.view.web.app).
    '''
	def __init__(self, pages, fvars={}, autoreload=None):
		web.application.__init__(self, fvars=fvars, autoreload=autoreload)
		mapping = []
		for p in pages:
			mapping.append(p.path)
			mapping.append(p.app)
		self._init_mapping(tuple(mapping))
