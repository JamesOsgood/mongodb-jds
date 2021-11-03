from datetime import datetime
from JDSBaseTest import JDSBaseTest

import pymongo

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		pipeline = [
			{
				'$group': {
					'_id': {
						'sku': '$sku', 
						'fascia': '$fascia'
					}, 
					'cnt': {
						'$sum': 1
					}, 
					'qtyATS': {
						'$sum': '$qtyATS'
					}, 
					'stock': {
						'$push': {
							'loc': '$loc', 
							'qtyATS': '$qtyATS'
						}
					}
				}
			}, {
				'$out': 'brstck_by_sku_fascia'
			}
		]
		ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
	
	def validate(self):
		pass
