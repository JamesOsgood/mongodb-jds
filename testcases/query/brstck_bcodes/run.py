from datetime import datetime
from JDSBaseTest import JDSBaseTest

import pymongo
import json

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		current_ids = []
		cnt = 0
		for doc in db.brstck.find({}, {'_id : 1'}).skip(770):
			current_ids.append(doc['_id'])
			self.log.info(doc['_id'])
			if len(current_ids) == 1:
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
					#, {
					# 	'$out': 'brstck_bcodes'
					# }
				]
				ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
				cnt += len(current_ids)
				current_ids = []
				self.log.info(f'Done {cnt}')
	
	def validate(self):
		pass
