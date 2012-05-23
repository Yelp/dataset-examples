from __future__ import with_statement
from unittest import TestCase
from StringIO import StringIO
import unittest
import json


from category_predictor import CategoryPredictor


# These templates can be used to make a json string very easily.
REVIEW_TEMPLATE = '{"type":"review", "stars":3, "text":"%s", "business_id":"%s"}\n'
BUSINESS_TEMPLATE= '{"type":"business", "categories":["%s"], "business_id":"%s"}\n' 
TEXT = "Hello world" * 101

class TestCategoryPredictor(TestCase):
	
	def test_smoke(self):
		"""Does a complete run with mock data"""
		category = 'Company'
		business_id = "Yelp"
		business = BUSINESS_TEMPLATE % (category, business_id)
		review = REVIEW_TEMPLATE % (TEXT, business_id)
		total_input = business + review
		static_stdin = StringIO(total_input)

		job = CategoryPredictor(['-r', 'inline', '--no-conf', '-'])
		job.sandbox(stdin=static_stdin)

		results = []
		with job.make_runner() as runner:
			runner.run()
			for line in runner.stream_output():
				key, value = job.parse_output_line(line)
				results.append(value)
		
		# Results should be the probability of that category being chosen. 1 category, 100% chance
		result = {category: 1}
		self.assertEqual(results[0], result)

	def test_review_category(self):
		"""Tests the category_mapper to make sure it is properly running"""
		business = BUSINESS_TEMPLATE % ('Company', "Yelp")
		review = REVIEW_TEMPLATE % ("Hello", "Yelp")
		
		job = CategoryPredictor()
		self.assertEqual(job.review_category_mapper(None, json.loads(review)).next(), 
							   (u'Yelp', ('review', u'Hello'))) 
		self.assertEqual(job.review_category_mapper(None, json.loads(business)).next(), 
							   (u'Yelp', ('categories', [u'Company'])))

	def test_categories_to_reviews(self):
		"""Tests add_categories_to_reviews to make sure it is properly running"""
		category = [('categories', ['Company']), ('review', 'Hello')]
		business_id = "Yelp"
		
		job = CategoryPredictor()
		result = ('all', {'Company': 1})
		self.assertEqual(job.add_categories_to_reviews_reducer(business_id, category).next(), result)

	def test_tokenize_reviews(self):
		"""Tests tokenize_reviews_mapper to make sure it is properly running"""
		category = 'all'
		review = {'Company': 1}
		
		job = CategoryPredictor()
		result = ('all', {'Company': 1})
		self.assertEqual(job.tokenize_reviews_mapper(category, review).next(), result)

	

if __name__ == '__main__':
	unittest.main()
