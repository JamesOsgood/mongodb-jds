from datetime import datetime
from JDSBaseTest import JDSBaseTest

import pymongo

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		non_matched_skus = set([])
		ITEMS_TO_PROCESS = 10
		# for update in db.diffs.find({}).sort([('ts', pymongo.DESCENDING)]).limit(ITEMS_TO_PROCESS):
		for update in db.brstck.find({}).limit(ITEMS_TO_PROCESS):
			sku = update['sku']
			loc = update['loc']
			fascia = update['fascia']
			# Find product
			product = self.get_sku_product_details(db, sku)
			if product:
				# Update quantity
				prev_qty = int(product['skus'][0]['qty'])
				new_qty = prev_qty + int(update['qtyATS'])
				self.log.info(f'sku: {sku}, loc {loc}, product qty {prev_qty}, new qty {new_qty}')

			else:
				if not sku in non_matched_skus:
					non_matched_skus.add(sku)
					self.log.warn(f'No Matching product for sku {sku}')

			
	def get_sku_product_details(self, db, sku):
		pipeline = [
				{
					'$match': {
						'skus.sku.id': sku
					}
				}, {
					'$project': {
						'id': 1, 
						'skus': {
							'$filter': {
								'input': '$skus.sku', 
								'as': 'item', 
								'cond': {
									'$eq': [
										'$$item.id', sku
									]
								}
							}
						}
					}
				}
			]
	
		ret = list(db.products.aggregate(pipeline))
		if len(ret) > 0:
			return ret[0]
		else:
			return None
	
	def validate(self):
		pass
