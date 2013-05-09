import imp
import os
import glob
from ...config import Config
from ...utils import Utils

conf = Config('avahi/external_filters.conf')
utils = Utils()
logging = utils.get_logging()

def import_source(name, path):
	logging.debug('import_source'+str((name, path)))
	try:
		return imp.load_source(name, path)
	except:
		return None

def get_filter_from(path, mod_name, class_name):
	logging.debug('get_filter_from:\npath: %s\nmodule: %s\nclass: %s' % (path,mod_name,class_name))
	if class_name: name = mod_name+'.'+class_name
	f = open(path, 'r')
	try:
		mod = imp.load_module(name, f, path, )
	finally:
		f.close()
	filter_obj = mod()
	del mod
	return filter_obj

def get_internal_filters():
	filters = []
	for f in glob.glob(os.path.dirname(__file__)+"/*.py"):
		if not f.endswith('__init__.py'):
			filters.append(get_filters_from(f))

def get_external_filters():
	filters = []
	external_filters = conf.get('external_filters_dir', set_type='config_dir')
	if not external_filters: return filters
	for c in external_filters:
		path = c.get('filter_path')
		module_name = os.path.splitext(os.path.basename(path))[0]
		class_name = c.get('class_name')
		if os.path.exists(path):
			try:
				filters.append(get_filter_from(path, module_name, class_name))
			except ImportError as e:
				logging.error(e)
	return filters

def get_all_filters():
	filters = []
	filters += get_internal_filters()
	logging.debug('internal filters: '+str(filters))
	filters += get_external_filters()
	logging.debug('internal and external filters: '+str(filters))
	return filters

all = get_all_filters()
__all__ = [ 'all' ]

if __name__ == '__main__':
	print('testing get_all_filters')
	print(get_all_filters())
