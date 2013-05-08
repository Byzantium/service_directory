import imp
import os
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

def get_filters_from(dirname):
	logging.debug('get_filters_from '+dirname)
	filters = []
	for module in os.listdir(dirname):
		if module != '__init__.py'  and module[-3:] == '.py':
			mod = import_source(module[:-3], module)
			logging.debug(dir(mod))
			if 'Filter' in dir(mod): filters.append(mod.Filter())
	del module
	return filters

def get_internal_filters():
	return get_filters_from(os.path.dirname(__file__))

def get_external_filters():
	filters = []
	external_filters = conf.get('external_filters')
	if not external_filters: return filters
	for name,path in external_filters.items():
		if os.path.isdir(path):
			filters += get_filters_from(path)
		else:
			mod = import_source()
			if 'Filter' in dir(mod):
				filters.append(mod.Filter())
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
