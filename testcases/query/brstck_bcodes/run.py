from datetime import datetime
from JDSBaseTest import JDSBaseTest

import pymongo
import json

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		db.brstck_bcodes.drop()
		current_ids = []
		BATCH_SIZE = 1000
		cnt = 0
		for doc in db.brstck.find({}, {'_id : 1'}, batch_size = BATCH_SIZE):
			current_ids.append(doc['_id'])
			# self.log.info(doc['_id'])
			if len(current_ids) == BATCH_SIZE:
				pipeline = self.get_pipeline(current_ids)
				ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
				cnt += len(current_ids)
				current_ids = []
				self.log.info(f'Done {cnt}')
	
	def get_pipeline(self, current_ids):
		pipeline = [
			{
				'$match': {
					'_id' : {
						'$in' : current_ids
					}
				}
			}, 
			{
				'$lookup': {
					'from': 'products', 
					'localField': 'sku', 
					'foreignField': 'skus.sku.id', 
					'as': 'product'
				}
			}, {
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$project': {
					'loc': 1, 
					'qtyATS': 1, 
					'sku': 1, 
					'product': {
						'$filter': {
							'input': '$product.skus.sku', 
							'as': 'item', 
							'cond': {
								'$eq': [
									'$$item.id', '$sku'
								]
							}
						}
					}
				}
			}, 
			{
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$project': {
					'loc': 1, 
					'qtyATS': 1, 
					'sku': 1, 
					'product': {
						'$filter': {
							'input': '$product.upcs.upc', 
							'as': 'item', 
							'cond': {
								'$eq': [
									'$$item.type', 'ean-13'
								]
							}
						}
					}
				}
			}, {
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$project': {
					'loc': 1, 
					'qty': '$qtyATS', 
					'sku': 1, 
					'bcode': '$product.value', 
					'_id': 0
				}
			}
			, {
				'$merge': {
					'into' : 'brstck_bcodes'
				}
			}
		]
		return pipeline

	def validate(self):
		pass
