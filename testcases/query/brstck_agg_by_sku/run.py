from datetime import datetime
from JDSBaseTest import JDSBaseTest

import pymongo

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		# limit = 10000
		pipeline = [
			# {
			# 	'$limit': 10
			# }, 
			{
				'$group': {
					'_id': {
						'sku': '$sku'
					}, 
					'cnt': {
						'$sum': 1
					}, 
					'qtyATS': {
						'$sum': '$qtyATS'
					}
				}
			}, {
				'$out': 'brstck_by_sku'
			}
		]
		ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
	
	def validate(self):
		pass
