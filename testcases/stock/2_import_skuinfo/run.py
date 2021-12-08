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
		sub_dir = 'latest'
		data_dir = os.path.join(os.path.expanduser(self.project.DATA_PATH), 'stock', sub_dir)
		skuinfo_file = os.path.join(data_dir, 'SKUInfo_ALLSites_TAB.txt')

		self.importFileMongoImport(skuinfo_file, 'skuinfo', type='tsv', columnsHaveTypes=True)


	def clear_all(self, db):
		db.skuinfo.drop()

	def validate(self):
		pass
