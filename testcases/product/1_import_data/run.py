import os
from datetime import datetime
import xmltodict
from pysys.constants import FOREGROUND


from JDSBaseTest import JDSBaseTest
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		self.clear_all(db)
		sub_dir = 'extracts'
		data_dir = os.path.join(os.path.expanduser(self.project.DATA_PATH), 'product', sub_dir)
		
		file_index = 0
		for filename in os.listdir(data_dir):
			self.log.info(f'{file_index} {filename}')
			if filename.endswith("csv"):
				path = os.path.join(data_dir, filename)
				coll_name = os.path.splitext(filename)[0]
				self.importFileMongoImport(path, coll_name)


	def clear_all(self, db):
		collections = db.command( {'listCollections': 1.0, 'nameOnly': True } )
		for coll_name in collections:
			if coll_name.startswith('raw.'):
				coll = db.get_collection(coll_name)
				coll.drop()

	def validate(self):
		pass
