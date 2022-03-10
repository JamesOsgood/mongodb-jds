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
		db = self.get_db_connection('jds_raw')
		# sub_dir = 'extracts'
		# data_dir = os.path.join(os.path.expanduser(self.project.DATA_PATH), 'product', sub_dir)
		
		# file_index = 0
		# for filename in os.listdir(data_dir):
		# 	self.log.info(f'{file_index} {filename}')
		# 	if filename.endswith("csv"):
		# 		path = os.path.join(data_dir, filename)
		# 		coll_name = os.path.splitext(filename)[0]
		# 		self.importFileMongoImport(path, coll_name, connectionString=self.project.CONNECTION_STRING_IMPORT.replace('~', '='))

		self.create_indexes(db)


	def create_indexes(self, db):
		indexes = []
		indexes.append( ("sku_product", ["SKU"] ))
		indexes.append( ("gender", ["GENDER_ID"] ))
		indexes.append( ("category", ["CATEGORY_ID"] ))
		indexes.append( ("department", ["DEPARTMENT_ID"] ))
		indexes.append( ("brand", ["BRAND_ID"] ))
		indexes.append( ("colour", ["COLOUR"] ))
		indexes.append( ("product_info", ["PRODUCT_INFO_ID"] ))
		indexes.append( ("grp", ["GROUP_ID", "DEPARTMENT_ID"] ))
		indexes.append( ("product_facia_info", ["PRODUCT_INFO_ID", "FACIA_ID"] ))

		for index in indexes:
			coll_name = index[0]
			fields = index[1]
			coll = db.get_collection(coll_name)
			index_def = []
			for field in fields:
				index_def.append((field,1))

			self.log.info(f'Creating {index_def} on {coll_name}')
			coll.create_index(index_def)

	def validate(self):
		pass
