import os
from datetime import datetime
import pip
import xmltodict
from pysys.constants import FOREGROUND


from JDSBaseTest import JDSBaseTest
from datetime import datetime

class PySysTest(JDSBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		JDSBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection('jds_product')
		input_coll = db.product

		output_coll_name = "product_search"

		pipeline = [ {
			'$project': {
				'CONCAT_INFO': {
					'$split': [
						'$CONCAT_INFO', '|'
					]
				}, 
				'TITLE': '$product_infoDetail.TITLE', 
				'BRAND_NAME': '$brandDetail.BRAND_NAME', 
				'MAIN_COLOUR': '$product_infoDetail.MAIN_COLOUR', 
				'SECONDARY_COLOUR': '$product_infoDetail.SECONDARY_COLOUR', 
				'FABRIC': '$product_infoDetail.FABRIC', 
				# 'UNK2': '', 
				'CARE': '$product_infoDetail.CARE', 
				'CATEGORY_DESC': '$categoryDetail.CATEGORY_DESC'
			}
			}, {
				'$out': output_coll_name
			}
		]
		
		input_coll.aggregate(pipeline)


	def validate(self):
		pass
