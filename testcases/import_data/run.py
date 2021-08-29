import os
from datetime import datetime
import xmltodict

import json

from JDSBaseTest import JDSBaseTest
import pymongo
import string
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

		self.importers = {}
		self.importers['Diff_Store_Stock_'] = self.import_diff
		# self.importers['JD_XML-BRSTCK_'] = self.import_brstck
		# self.importers['Shogun_pimimport_stock_'] = self.import_shogun_stock
		# self.importers['Shogun_pimimport_price_'] = self.import_shogun_price
		self.importers['Shogun_pimimport_product_'] = self.import_shogun_product
		self.BATCH_SIZE = 1000
		self.docs = []
		self.doc_count = 0

	def execute(self):
		db = self.get_db_connection()
		self.clear_all(db)
		sub_dir = 'latest'
		data_dir = os.path.join(os.path.expanduser(self.project.DATA_PATH), sub_dir)
		
		for filename in os.listdir(data_dir):
			self.log.info(filename)
			if filename.endswith("xml"):
				docs = []
				for stub in self.importers.keys():
					if filename.startswith(stub):
						ts = self.extract_date(filename, stub)
						with open(os.path.join(data_dir, filename)) as file:					
							self.importers[stub](db, ts, file)

	def done_file(self, collection):
		if len(self.docs) > 0:
			self.doc_count += len(self.docs)
			collection.insert_many(self.docs)
			self.log.info(f"Inserted {self.doc_count} into {collection.name}")
		self.docs = []
		self.doc_count = 0

	def add_doc(self, collection, doc):
		self.docs.append(doc)
		if len(self.docs) == self.BATCH_SIZE:
			self.doc_count += len(self.docs)
			collection.insert_many(self.docs)
			self.log.info(f"Inserted {self.doc_count} into {collection.name}")
			self.docs = []

	def extract_date(self, filename, stub):
		stub_len = len(stub)
		date_str = filename[stub_len: stub_len + 12]
		self.log.info(date_str)
		return datetime.strptime(date_str, '%Y%m%d%H%M')
		
	def import_diff(self, db, ts, file):
		positions = xmltodict.parse(file.read())
		for position in positions['inventoryPositions']['inventoryPosition']:
			position['ts'] = ts
			sku = position['sku']
			position['sku'] = sku.rjust(9, '0')
			self.add_doc(db.raw.diffs, position)

		self.done_file(db.raw.diffs)

	def import_brstck(self, db, ts, file):
		positions = xmltodict.parse(file.read())
		for position in positions['inventoryPositions']['inventoryPosition']:
			position['ts'] = ts
			sku = position['sku']
			position['sku'] = sku.rjust(9, '0')
			self.add_doc(db.raw.brstck, position)

		self.done_file(db.raw.brstck)

	def import_shogun_stock(self, db, ts, file):
		products = xmltodict.parse(file.read())
		converted_sku = 0
		products_seen = set()
		for product in products['products']['product']:
			id = product['id']
			if not id in products_seen:
				product['ts'] = ts
				skus = product['skus']['sku']
				if not isinstance(skus, list):
					converted_sku += 1
					self.log.info(f'Converting to list: {converted_sku}')
					product['skus']['sku'] = [skus]

				self.add_doc(db.raw.stock, product)
				products_seen.add(id)

		self.done_file(db.raw.stock)

	def import_shogun_price(self, db, ts, file):
		products = xmltodict.parse(file.read())
		converted_sku = 0
		products_seen = set()
		for product in products['products']['product']:
			id = product['id']
			if not id in products_seen:
				product['ts'] = ts
				skus = product['skus']['sku']
				if not isinstance(skus, list):
					converted_sku += 1
					self.log.info(f'Converting to list: {converted_sku}')
					product['skus']['sku'] = [skus]

				self.add_doc(db.raw.prices, product)
				products_seen.add(id)

		self.done_file(db.raw.prices)

	def import_shogun_product(self, db, ts, file):
		products = xmltodict.parse(file.read())
		converted_sku = 0
		converted_upc = 0
		products_seen = set()
		for product in products['products']['product']:
			id = product['id']
			self.log.info(id)
			if not id in products_seen:
				product['ts'] = ts
				skus = product['skus']['sku']
				if not isinstance(skus, list):
					
					converted_sku += 1
					self.log.info(f'Converting to list: {converted_sku}')
					product['skus']['sku'] = [skus]

				for sku in product['skus']['sku']:
					upcs = sku['upcs']['upc']
					self.log.info(upcs)
					if not isinstance(upcs, list):
						converted_upc += 1
						self.log.info(f'Converting upc to list: {converted_upc}')
						sku['upcs']['upc'] = [upcs]

				self.add_doc(db.raw.products, product)
				products_seen.add(id)

		self.done_file(db.raw.products)

	def clear_all(self, db):
		db.raw.diff.drop()
		db.raw.brstck.drop()
		db.raw.products.drop()
		db.raw.stock.drop()
		db.raw.prices.drop()

	def validate(self):
		pass
