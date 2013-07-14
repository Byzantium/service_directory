from byzantium.avahi.service_index import ServiceIndex,Record
si = ServiceIndex()

def test_services_py():
	'''
		load test data for services.py
	'''
	fake_record = Record(interface=0,protocol=0,service_name='test_service_name',service_type='_test_service_type',service_domain='_test_service_domain', hostname='test_hostname', ip_version=6, ipaddr='::1', port=9001, txt='description=test service description\nappendtourl=hello?test=service\nshow=user')
	si.add(fake_record)
	si.push() # replace anything that could be in the service directory
	si.pull() # load the contents of the service directory
	print(repr(si.dump())) # show what is there

if __name__ == '__main__':
	test_services_py()
