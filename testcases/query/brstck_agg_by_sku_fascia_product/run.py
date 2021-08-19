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
				'$lookup': {
					'from': 'products', 
					'localField': '_id.sku', 
					'foreignField': 'skus.sku.id', 
					'as': 'product'
				}
			}, {
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$project': {
					'_id': 1, 
					'cnt': 1, 
					'qtyATS': 1, 
					'product_sku': '$product.id', 
					'stock': 1
				}
			}, {
				'$out': 'brstck_by_sku_fascia_product'
			}
		]
		ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
	
	def validate(self):
		pass
