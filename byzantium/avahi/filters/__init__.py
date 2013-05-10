import imp
import os
import glob
from byzantium.config import Config
from byzantium.utils import Utils

class _Filters(list):
	def __init__(self):
		self.conf = Config('avahi/external_filters.conf')
		self.utils = Utils()
		self.logging = self.utils.get_logging()
		self.all_filters = self.get_all_filters()

	def __contains__(self, item):
		return self.all_filters.__contains__(item)

	def __missing__(self, item):
		return self.all_filters.__missing__(item)

	def __getitem__(self, key):
		return self.all_filters.__getitem__(key)

	def __iter__(self):
		return self.all_filters.__iter__()

	def next(self):
		return self.all_filters.next()

	def __len__(self):
		return self.all_filters.__len__()

	def count(self, i):
		 return self.all_filters.count()

	def index(self, i):
		return self.all_filters.index(i)

	def pop(self, i=-1):
		if len(self.all_filters) > 0 and len(self.all_filters) > i:
			return self.all_filters[i]
		else:
			return None

	def reverse(self):
		return self.all_filters.reverse()

	def sort(self):
		return self.all_filters.sort()

	def get_filter_from(self, path, mod_name, class_name=None):
		print('get_filter_from:\npath: %s\nmodule: %s\nclass: %s' % (path,mod_name,class_name))
		self.logging.debug('get_filter_from:\npath: %s\nmodule: %s\nclass: %s' % (path,mod_name,class_name))
		path_dir = os.path.dirname(path)
		if os.path.isdir(path): path_dir = path
		f=open('/dev/null','r')
		try:
			f, filename, description = imp.find_module(mod_name, path_dir)
			mod = imp.load_module(mod_name, f, filename, description)
			if class_name:
				mod_path = mod.__path__
				submod = '%s.%s' % (mod_name,class_name)
				if mod_name == __name__:
					mod_path = os.path.join(mod.__path__, __name__)
					submod = class_name
				sf, filename, description = imp.find_module(class_name, mod_path)
				try:
					mod = imp.load_module(submod, sf, filename, description)
				finally:
					sf.close()
		finally:
			f.close()
		filter_obj = mod()
		return filter_obj

	def get_internal_filters(self):
		filters = []
		for f in glob.glob(os.path.dirname(__file__)+"/*.py"):
			if not f.endswith('__init__.py'):
				mod = os.path.splitext(os.path.basename(f))[0]
				filters.append(self.get_filter_from(path=__file__,mod_name=mod))
		self.all_filters.extend(filters)

	def get_external_filters(self):
		filters = []
		external_filters = self.conf.get('external_filters_dir', set_type='config_dir')
		if not external_filters: return filters
		for c in external_filters:
			path = c.get('filter_path')
			module_name = os.path.splitext(os.path.basename(path))[0]
			class_name = c.get('class_name')
			if os.path.exists(path):
				try:
					filters.append(self.get_filter_from(path, module_name, class_name))
				except ImportError as e:
					logging.error(e)
		self.all_filters.extend(filters)

	def get_all_filters(self):
		self.get_internal_filters()
		self.get_external_filters()


sys.modules[__name__] = _Filters()
