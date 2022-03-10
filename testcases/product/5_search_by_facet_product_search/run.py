from datetime import datetime
from random import random
from pysys.constants import FOREGROUND
import random

from JDSBaseTest import JDSBaseTest
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection('jds_product')
		input_coll = db.product_search

		all_facet_values = self.get_facet_values(self.get_all_facet_counts(input_coll))
		ITERATIONS = 1
		FACETS_TO_PICK = 2
		for i in range(ITERATIONS):
			facets = random.sample(all_facet_values.keys(),FACETS_TO_PICK)
			facet_values = {}
			for facet in facets:
				facet_values[facet] = all_facet_values[facet]

			docs = self.get_data_and_counts(input_coll, facet_values)

	def get_data_and_counts(self, input_coll, facet_values):
		must = []
		facets = {}
		for field in facet_values:
			values = facet_values[field]
			
			# Must
			text_doc = {}
			text_doc['text'] = {}
			text_doc['text']['query'] = random.choice(values)
			text_doc['text']['path'] = field
			must.append(text_doc)

			# facets
			facet_doc = {}
			facet_doc['type'] = 'string'
			facet_doc['path'] = field
			facets[field] = facet_doc

		pipeline_data = [
			{
				'$search': {
					'index': 'default', 
					'compound': {
						'must': must
					}
				}
			},
			{ '$count' : 'cnt' }
		]


		res = list(input_coll.aggregate(pipeline_data))
		cnt = 0
		if len(res) > 0:
			cnt = res[0]['cnt']
		self.log.info(f"Pipeline {pipeline_data} returned {cnt} results")

		filter = { 'compound': { 'must': must } }
		facet_counts = self.get_facet_counts(input_coll, filter)

		for field in facet_counts:
			self.log.info(f"OUTPUT: {field} ({len(facet_counts[field]['buckets'])})")

	def get_all_facet_counts(self, input_coll):
		exists = {}
		exists['exists'] = {'path': 'BRAND_NAME'}
		return self.get_facet_counts(input_coll, exists)

	def get_facet_counts(self, input_coll, operator, limit = 100):
		pipeline = [{
			'$searchMeta': {
				'index': 'default', 
				'facet': {
					'operator': operator,
					'facets': {
						'BRAND_NAME': {
							'type': 'string', 
							'path': 'BRAND_NAME',
							'numBuckets' : limit
						}, 
						'TITLE': {
							'type': 'string', 
							'path': 'TITLE',
							'numBuckets' : limit
						}, 
						'MAIN_COLOUR': {
							'type': 'string', 
							'path': 'MAIN_COLOUR',
							'numBuckets' : limit
						}, 
						'SECONDARY_COLOUR': {
							'type': 'string', 
							'path': 'SECONDARY_COLOUR',
							'numBuckets' : limit
						}, 
						'FABRIC': {
							'type': 'string', 
							'path': 'FABRIC',
							'numBuckets' : limit
						}, 
						'CARE': {
							'type': 'string', 
							'path': 'CARE',
							'numBuckets' : limit
						}, 
						'CATEGORY_DESC': {
							'type': 'string', 
							'path': 'CATEGORY_DESC',
							'numBuckets' : limit
						}
					}
				}
			}
		}]

		ret = list(input_coll.aggregate(pipeline))
		if len(ret) > 0:
			ret = ret[0]
			return ret['facet']
		return None


	def get_facet_values(self, facets):
		facet_values = {}
		for key in facets.keys():
			facet = facets[key]
			values = []
			facet_values[key] = values
			for bucket in facet['buckets']:
				values.append(bucket['_id'])
		return facet_values

	def validate(self):
		pass