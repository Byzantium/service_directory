import imp
import os
import glob
import sys
from byzantium.config import Config
from byzantium.utils import Utils

SYS_PATH_ORIG = [x for x in sys.path]

filters_dir = 'filters_d'	# internally defined filters dir in byzantium.avahi

class Filters(list):
	def __init__(self):
		self.conf = Config('avahi/external_filters.conf')
		self.utils = Utils()
		self.logger = self.utils.get_logger()
		self.all_filters = []
		self.get_all_filters()

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

	def _raw_import(self, mod_name):
		print(sys.path)
		try:
			mod = __import__(mod_name)
			return mod
		except ImportError as e:
			self.logger.error(e)
			return None

	def _try_import(self, mod_name, path=[]):
		have_set_path = False
		warn_not_found = 'module "%s" not found' % mod_name
		try:
			if path and type(path) != list:
				path = [str(path)]
			if path:
				have_set_path = True
				sys.path = path
			mod = self._raw_import(mod_name)
			if not mod and have_set_path:
				sys.path = SYS_PATH_ORIG
				mod = self._raw_import(mod_name)
				if not mod:
					self.logger.warn(warn_not_found)
					return None
			return mod
		finally:
			sys.path = SYS_PATH_ORIG

	def get_filter_from(self, path='.', mod_name=None, class_name=None):
		print('get_filter_from:\npath: %s\nmodule: %s\nclass: %s' % (path, mod_name, class_name))
		self.logger.debug('get_filter_from:\npath: %s\nmodule: %s\nclass: %s' % (path, mod_name, class_name))
		if path:
			path_dir = os.path.dirname(path)
			if os.path.isdir(path): path_dir = path
		else:
			path_dir = None
		try:
			mod = self._try_import(mod_name, path_dir)
			if mod and class_name:
				submod = getattr(mod,class_name)
				print(mod,submod)
				if submod: return submod
			return mod
		except ImportError as e:
			self.logger.error(e)
			self.logger.warn('module.class "%s.%s" not found' % (mod_name, class_name))
		return None

	def get_internal_filters(self):
		for f in glob.glob(os.path.join(os.path.dirname(__file__), filters_dir)+'/*.py'):
			if not f.endswith('__init__.py'):
				if not os.path.isdir(f):
					path = os.path.dirname(f)
				else:
					path = f
				mod = os.path.splitext(os.path.basename(f))[0]
				filter_mod = self.get_filter_from(mod_name=mod, path=path)
				if filter_mod: self.all_filters.append(filter_mod)

	def get_external_filters(self):
		print('get_external_filters:')
		external_filters = self.conf.get('avahi/external_filters.d', set_type='config_dir')
		print(external_filters) #DELETEME
		if not external_filters or type(external_filters) != list: return None
		for c in external_filters:
			print(c.get('filter_path'), c.get('class_name')) #DELETEME
			path = c.get('filter_path')
			print('path', path)
			if path:
				print('path not empty')
				module_name = os.path.splitext(os.path.basename(path))[0]
				class_name = c.get('class_name')
				print(module_name, class_name, path)
				if os.path.exists(path):
					print('path exists')
					try:
						filter_mod = self.get_filter_from(path, module_name, class_name)
						print(filter_mod)
					except ImportError as e:
						self.logger.error(e)
						filter_mod = None
					if filter_mod:
						self.all_filters.append(filter_mod)

	def get_all_filters(self):
		self.get_internal_filters()
		self.get_external_filters()
