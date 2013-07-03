import unittest
from byzantium.avahi.service_index import ServiceIndex, Index

test_dict = {'test':{'hello':'world'}, 'alice':{'bob':'eve'}}
remove_end_dict = {'alice': {'bob': 'eve'}}

class TestServiceIndex(unittest.TestCase):
	def setUp(self):
		self.si = ServiceIndex()
	def test_dump(self):
		index = self.si.dump()
		self.assertEqual(type(index), type(Index()))
		self.assertEqual(index.data, {})
	def test_update(self):
		self.si.update(test_dict)
		index = self.si.dump()
		self.assertEqual(index.data, test_dict)
	def test_remove(self):
		self.si.remove('test')
		index = self.si.dump()
		self.assertEqual(index.data, remove_end_dict)

if __name__ == '__main__':
	unittest.main()
