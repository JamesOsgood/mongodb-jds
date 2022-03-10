import os
from datetime import datetime
import pip
import xmltodict
from pysys.constants import FOREGROUND


from JDSBaseTest import JDSBaseTest
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection('jds_product')
		input_coll = db.product

		SAMPLE_SIZE = 10

		pipeline = [ {
				'$sample': {
					'size': SAMPLE_SIZE
				}
			}, {
				'$project': {
					'_id': 0, 
					'BARCODE_PRIMARY': 1
				}
			}
		]
		barcodes = []
		for doc in input_coll.aggregate(pipeline):
			barcodes.append(doc['BARCODE_PRIMARY'])

		for barcode in barcodes:
			self.log.info(f'Looking up barcode {barcode}')
			doc = db.product.find_one({'BARCODE_PRIMARY' : barcode})
			self.log.info(f'Found doc {doc["_id"]}')


	def validate(self):
		pass
