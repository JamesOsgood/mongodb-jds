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
		input_coll = db.product

		all_facet_values = self.get_facet_values(self.get_all_facet_counts(input_coll))
		titles = all_facet_values['product_infoDetail.TITLE']

		input_value = random.choice(titles)
		if len(input_value) > 3:
			input_value = input_value[0:5]

		self.get_data(input_coll, input_value)


	def get_data(self, input_coll, input_value):

		pipeline_data = [
			{
				'$search': {
					'index': 'autocompleteIndex', 
					'autocomplete': {
						'query': input_value, 
						'path': 'product_infoDetail.TITLE'
					}
				}
			}, {
				'$project': {
					'TITLE': '$product_infoDetail.TITLE', 
					'SKU_SIZE': 1, 
					'GENDER_ID': 1, 
					'COLOUR_ID': 1, 
					'_id': 0, 
					'PRODUCT_INFO_ID': 1, 
					'score': {
						'$meta': 'searchScore'
					}
				}
			}, {
				'$limit': 25
			}
		]


		res = list(input_coll.aggregate(pipeline_data))
		cnt = 0
		if len(res) > 0:
			cnt = len(res)
		self.log.info(f"Pipeline returned {cnt} results")
		self.log.info(f"\t\tMDB:{pipeline_data}")

	def get_all_facet_counts(self, input_coll):
		exists = {}
		exists['exists'] = {'path': 'brandDetail.BRAND_NAME'}
		return self.get_facet_counts(input_coll, exists)

	def get_facet_counts(self, input_coll, operator, limit = 100):
		pipeline = [{
			'$searchMeta': {
				'index': 'facetIndex', 
				'facet': {
					'operator': operator,
					'facets': {
						'brandDetail.BRAND_NAME': {
							'type': 'string', 
							'path': 'brandDetail.BRAND_NAME',
							'numBuckets' : limit
						}, 
						'product_infoDetail.TITLE': {
							'type': 'string', 
							'path': 'product_infoDetail.TITLE',
							'numBuckets' : limit
						}, 
						'product_infoDetail.MAIN_COLOUR': {
							'type': 'string', 
							'path': 'product_infoDetail.MAIN_COLOUR',
							'numBuckets' : limit
						}, 
						'product_infoDetail.SECONDARY_COLOUR': {
							'type': 'string', 
							'path': 'product_infoDetail.SECONDARY_COLOUR',
							'numBuckets' : limit
						}, 
						'product_infoDetail.FABRIC': {
							'type': 'string', 
							'path': 'product_infoDetail.FABRIC',
							'numBuckets' : limit
						}, 
						'product_infoDetail.CARE': {
							'type': 'string', 
							'path': 'product_infoDetail.CARE',
							'numBuckets' : limit
						}, 
						'categoryDetail.CATEGORY_DESC': {
							'type': 'string', 
							'path': 'categoryDetail.CATEGORY_DESC',
							'numBuckets' : limit
						}
					}
				}
			}
		}]

		self.log.info(pipeline)
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
