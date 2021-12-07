import os
from datetime import datetime
import xmltodict

import csv
import json

from JDSBaseTest import JDSBaseTest
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

		self.importers = {}
		self.importers['categories'] = self.import_categories
		self.importers['custom_attributes_meta'] = self.import_custom_attributes_meta
		self.importers['custom_attributes_values'] = self.import_custom_attributes_values
		self.importers['custom_variant_attributes'] = self.import_custom_variant_attributes
		self.importers['products'] = self.import_products
		self.importers['variants'] = self.import_variants
		self.BATCH_SIZE = 1000
		self.docs = []
		self.doc_count = 0

	def execute(self):
		db = self.get_db_connection('search')
		self.clear_all(db)
		sub_dir = 'search'
		data_dir = os.path.join(os.path.expanduser(self.project.DATA_PATH), sub_dir)
		
		for filename in os.listdir(data_dir):
			self.log.info(filename)
			if filename.endswith("csv"):
				for stub in self.importers.keys():
					if filename.startswith(stub):
						with open(os.path.join(data_dir, filename)) as file:					
							self.importers[stub](db, file)

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
		
	def import_categories(self, db, file):

		self.csv_to_json(file, db.categories)
		self.done_file(db.categories)

	def import_custom_attributes_meta(self, db, file):

		self.csv_to_json(file, db.custom_attributes_meta)
		self.done_file(db.custom_attributes_meta)

	def import_custom_attributes_values(self, db, file):

		self.csv_to_json(file, db.custom_attributes_values)
		self.done_file(db.custom_attributes_values)

	def import_custom_variant_attributes(self, db, file):

		self.csv_to_json(file, db.custom_variant_attributes)
		self.done_file(db.custom_variant_attributes)

	def import_products(self, db, file):

		self.csv_to_json(file, db.products)
		self.done_file(db.products)

	def import_variants(self, db, file):

		self.csv_to_json(file, db.variants)
		self.done_file(db.variants)


	def csv_to_json(self, csvf, collection):
		
		self.log.info(f'Importing %s', collection.name)
		#load csv file data using csv library's dictionary reader
		csvReader = csv.DictReader(csvf, dialect='excel-tab') 

		#convert each csv row into python dict
		for row in csvReader: 
			converted ={}
			for field in row.keys():
				if field:
					if len(field) > 0:
						converted[field] = row[field]
			self.add_doc(collection,converted)
	
	def clear_all(self, db):
		db.categories.drop()
		db.custom_attributes_meta.drop()
		db.custom_attributes_values.drop()
		db.custom_variant_attributes.drop()
		db.products.drop()
		db.variants.drop()

	def validate(self):
		pass
