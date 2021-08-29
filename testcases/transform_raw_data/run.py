import os
from datetime import datetime
import xmltodict

import json

from JDSBaseTest import JDSBaseTest
import pymongo
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()

		agg_brstck = [
			{
				'$project': {
					'loc': 1, 
					'fascia': 1, 
					'sku': 1, 
					'qtyATS': {
						'$toInt': '$qtyATS'
					}, 
					'ts': 1
				}
			}, {
				'$out': 'brstck'
			}
		]
		self.log.info('raw.brstck')
		db.raw.brstck.aggregate(agg_brstck)

		agg_diffs = [
			{
				'$project': {
					'loc': 1, 
					'fascia': 1, 
					'sku': 1, 
					'qtyATS': {
						'$toInt': '$qtyATS'
					}, 
					'ts': 1
				}
			}, {
				'$out': 'diffs'
			}
		]
		self.log.info('raw.diffs')
		db.raw.diffs.aggregate(agg_diffs)

		agg_products = [
			{
				'$out': 'products'
			}
		]
		self.log.info('raw.products')
		db.raw.products.aggregate(agg_products)

		agg_prices = [
			{
				'$out': 'prices'
			}
		]
		self.log.info('raw.prices')
		db.raw.prices.aggregate(agg_prices)

		agg_stock = [
			{
				'$out': 'stock'
			}
		]
		self.log.info('raw.stock')
		db.raw.stock.aggregate(agg_stock)

	def validate(self):
		pass
