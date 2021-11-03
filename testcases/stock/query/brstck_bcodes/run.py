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
		db.batch_done.delete_many({})
		db.batch_progress.delete_many({})
		db.batch_progress.insert_one({'batches_inserted' : 0, 'batches_sent' : 0, 'docs_inserted' : 0, 'docs_sent' : 0})
		current_ids = []
		BATCH_SIZE = 10000
		cnt = 0
		batch_index = 0
		for doc in db.brstck.find({}, {'_id : 1'}, batch_size = BATCH_SIZE):
			current_ids.append(doc['_id'])
			# self.log.info(doc['_id'])
			if len(current_ids) == BATCH_SIZE:
				pipeline = self.get_pipeline_skuinfo(current_ids, batch_index)
				ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
				cnt += len(current_ids)
				db.batch_progress.update_one({}, { '$inc' : { 'batches_inserted' : 1, 'docs_inserted' : len(current_ids), 'bcodes_inserted' : len(ret)}})
				db.batch_done.insert_one({'batch_index' : batch_index})
				batch_index += 1
				current_ids = []
				self.log.info(f'Done {cnt}')

		if len(current_ids) >0:
			pipeline = self.get_pipeline_skuinfo(current_ids, batch_index)
			ret = list(db.brstck.aggregate(pipeline, allowDiskUse=True))
			cnt += len(current_ids)
			db.batch_progress.update_one({}, { '$inc' : { 'batches_inserted' : 1, 'docs_inserted' : len(current_ids), 'bcodes_inserted' : len(ret)}})
			db.batch_done.insert_one({'batch_index' : batch_index})
			batch_index += 1
			current_ids = []
			self.log.info(f'Done {cnt}')
	
	def get_pipeline_skuinfo(self, current_ids, batch_index):
		pipeline = [
			{
				'$match': {
					'_id' : {
						'$in' : current_ids
					}
				}
		 	}, {
				'$lookup': {
					'from': 'skuinfo', 
					'localField': 'sku', 
					'foreignField': 'RemoteSystemId', 
					'as': 'product'
				}
			}, {
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$unwind': {
					'path': '$product'
				}
			}, {
				'$project': {
					'loc': 1, 
					'qty': {
						'$toString': '$qtyATS'
					}, 
					'sku': 1, 
					'bcode': '$product.Upc', 
					'_id': 0
				}
			}, {
				'$merge': {
					'into': 'brstck_bcodes'
				}
			}
		]		
		return pipeline

	def get_pipeline_product(self, current_ids, batch_index):
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
					'qty': { '$toString' : '$qtyATS' }, 
					'sku': 1, 
					'bcode': '$product.value', 
					'_id': 0
				}
			}, {
				'$addFields' : {
					'batch_index' : batch_index
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
