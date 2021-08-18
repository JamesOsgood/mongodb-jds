
import os
import time

from pymongo import MongoClient
from pysys.basetest import BaseTest

class JDSBaseTest(BaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		BaseTest.__init__(self, descriptor, outsubdir, runner)

		self.db_connection = None
		self.connectionString = self.project.CONNECTION_STRING.replace("~", "=")


	# open db connection
	def get_db_connection(self):
		if self.db_connection is None:
			self.log.info("Connecting to: %s" % self.connectionString)
			client = MongoClient(self.connectionString)
			self.db_connection = client.get_database()

		return self.db_connection

	# Run query
	def run_query(self, filter):
		db = self.get_db_connection()
		self.log.info(filter)
		for ret in db.docs.find(filter):
			self.log.info(f"Query returned documentid {ret['_id']}")

	def run_agg_query(self, pipeline):
		db = self.get_db_connection()
		for ret in db.docs.aggregate(pipeline):
			self.log.info(ret['_id'])

