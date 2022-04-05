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
		db = self.get_db_connection('jds_raw')
		input_coll = db.sku_product


		output_db = self.get_db_connection('jds_product')
		output_coll_name = "product"
		output_coll = output_db[output_coll_name]
		# output_coll.drop()

		BATCH_SIZE = 1
		cnt = 0
		current_ids = []
		for doc in input_coll.find({}, {'SKU' : 1}, batch_size = BATCH_SIZE):
			# self.log.info(doc)
			current_ids.append(doc['SKU'])
			# self.log.info(doc['SKU'])
			if len(current_ids) == BATCH_SIZE:
				self.create_productx(input_coll, current_ids)
				cnt += len(current_ids)
				current_ids = []
				self.log.info(f'Done {cnt}')
				break
		
		# self.create_indexes(output_coll)


	def create_productx(self, input_coll, current_ids):

		joins = []
		# Simple
		joins.append( ("gender", ["GENDER_ID", "GENDER_ID"] ))
		joins.append( ("category", ["CATEGORY_ID", "CATEGORY_ID"] ))
		joins.append( ("department", ["DEPARTMENT_ID", "DEPARTMENT_ID"] ))
		joins.append( ("brand", ["BRAND_ID", "BRAND_ID"] ))
		joins.append( ("colour", ["COLOUR", "COLOUR_ID"] ))
		joins.append( ("product_info", ["PRODUCT_INFO_ID", "PRODUCT_INFO_ID"] ))
		# # # Multi
		joins.append( ("grp", ["GROUP_ID", "GROUP_ID", "DEPARTMENT_ID", "DEPARTMENT_ID"] ))
		joins.append( ("product_facia_info", ["PRODUCT_INFO_ID", "PRODUCT_INFO_ID", "FACIA_ID", "_JD"] ))

		pipeline = []
		pipeline.append( { '$match': {
					'SKU': { '$in' : current_ids } 
				}
			})

		for join in joins:
			rhs = join[0]
			
			fields = join[1]
			if len(fields) == 2:
				lhs_field = fields[0]
				rhs_field = fields[1]
				self.addLookupStage(pipeline, rhs, lhs_field, rhs_field)
			elif len(fields) == 4:
				lhs_field_1 = fields[0]
				rhs_field_1 = fields[1]
				lhs_field_2 = fields[2]
				rhs_field_2 = fields[3]
				self.addLookupStageMultiple(pipeline, rhs, lhs_field_1, rhs_field_1, lhs_field_2, rhs_field_2)

		merge = {
				'$merge': {
					'into': { 'db' : 'jds_product', 
					          'coll' : 'product'
					}, 
					'on': '_id', 
					'whenMatched': 'merge'
				}
			}
		pipeline.append(merge)
		self.log.info(pipeline)
		# cnt = len(list(input_coll.aggregate(pipeline)))
		# self.log.info(cnt)

	def create_indexes(self, output_coll):
		output_coll.create_index('BARCODE_PRIMARY')

	def get_field_for_join(self, field):
		if field.startswith("_"):
			return field[1:]
		else:
			return f'${field}'

	def addLookupStageMultiple( self, pipeline, rhs, lhs_field_1, rhs_field_1, lhs_field_2, rhs_field_2):
		lookup = { '$lookup': {
					'from': rhs, 
					'let': {
						lhs_field_1.lower(): self.get_field_for_join(rhs_field_1), 
						lhs_field_2.lower(): self.get_field_for_join(rhs_field_2) 
					}, 
					'pipeline': [
						{
							'$match': {
								'$expr': {
									'$and': [
										{
											'$eq': [
												f'${lhs_field_1}', f'$${lhs_field_1.lower()}'
											]
										}, {
											'$eq': [
												f'${lhs_field_2}', f'$${lhs_field_2.lower()}'
											]
										}
									]
								}
							}
						}
					], 
					'as': f'{rhs}Detail'
				}
			}
		unwind = {
				'$unwind': {
					'path': f'${rhs}Detail',
					'preserveNullAndEmptyArrays': True
				}
			}
		pipeline.append(lookup)
		pipeline.append(unwind)

	def join_collection_multiple( self, coll, current_ids, rhs, lhs_field_1, rhs_field_1, lhs_field_2, rhs_field_2):
		
		pipeline = [
			{
				'$match': {
					'SKU': { '$in' : current_ids } 
				}
			}, {
				'$lookup': {
					'from': rhs, 
					'let': {
						lhs_field_1.lower(): self.get_field_for_join(rhs_field_1), 
						lhs_field_2.lower(): self.get_field_for_join(rhs_field_2) 
					}, 
					'pipeline': [
						{
							'$match': {
								'$expr': {
									'$and': [
										{
											'$eq': [
												f'${lhs_field_1}', f'$${lhs_field_1.lower()}'
											]
										}, {
											'$eq': [
												f'${lhs_field_2}', f'$${lhs_field_2.lower()}'
											]
										}
									]
								}
							}
						}
					], 
					'as': f'{rhs}Detail'
				}
			}, {
				'$unwind': {
					'path': f'${rhs}Detail',
					'preserveNullAndEmptyArrays': True
				}
			}, {
				'$merge': {
					'into': 'productx', 
					'on': '_id', 
					'whenMatched': 'merge'
				}
			}
		]
		# self.log.info(pipeline)
		coll.aggregate(pipeline)

	def addLookupStage( self, pipeline, rhs, lhs_field, rhs_field):
		lookup = { '$lookup': {
					'from': rhs, 
					'localField': lhs_field, 
					'foreignField': rhs_field, 
					'as': f'{rhs}Detail'}
				}
		unwind = {
				'$unwind': {
					'path': f'${rhs}Detail',
					'preserveNullAndEmptyArrays': True
				}
			}

		pipeline.append(lookup)
		pipeline.append(unwind)

	def join_collection( self, coll, current_ids, rhs, lhs_field, rhs_field):
		
		
		# self.log.info(f"{rhs}, {current_ids}")
		pipeline = [
			{
				'$match': {
					'SKU': { '$in' : current_ids } 
				}
			}, {
				'$lookup': {
					'from': rhs, 
					'localField': lhs_field, 
					'foreignField': rhs_field, 
					'as': f'{rhs}Detail'
				}
			}, {
				'$unwind': {
					'path': f'${rhs}Detail',
					'preserveNullAndEmptyArrays': True
				}
			}, {
				'$merge': {
					'into': 'productx', 
					'on': '_id', 
					'whenMatched': 'merge'
				}
			}
		]

		# if rhs == 'grp':
		# 	self.log.info(pipeline)
		coll.aggregate(pipeline)

	def join_collection2( self, coll, current_ids, rhs, lhs_field, rhs_field):
		pipeline = [
			{
				'$match': {
					'SKU': { '$in' : current_ids } 
				}
			}, {
				'$lookup': {
					'from': rhs, 
					'let': {
						lhs_field.lower(): self.get_field_for_join(rhs_field), 
					}, 
					'pipeline': [
						{
							'$match': {
								'$expr': {
									'$and': [
										{
											'$eq': [
												f'${lhs_field}', f'$${lhs_field.lower()}'
											]
										}
									]
								}
							}
						}
					], 
					'as': f'{rhs}Detail'
				}
			}, {
				'$unwind': {
					'path': f'${rhs}Detail'
				}
			}, {
				'$merge': {
					'into': 'productx', 
					'on': '_id', 
					'whenMatched': 'merge'
				}
			}
		]
		
		# if rhs == 'grp':
		# 	self.log.info(pipeline)
		coll.aggregate(pipeline)

	def validate(self):
		pass
