from __future__ import with_statement
from unittest import TestCase
from StringIO import StringIO
import unittest
import json

from category_predictor import CategoryPredictor

# These templates can be used to make a json string very easily.
REVIEW_TEMPLATE = '{"type":"review", "stars":3, "text":"%s",\
"business_id":"%s"}\n'
BUSINESS_TEMPLATE = '{"type":"business", "categories":["%s"], \
"business_id":"%s"}\n'
LONG_TEXT = "Hello world" * 101
TEXT = u"Hello"
BIZ_ID = u"Yelp"
CATEGORIES = u'Company'


class TestCategoryPredictor(TestCase):

	def test_smoke(self):
		"""Does a complete run with mock data"""
		business = BUSINESS_TEMPLATE % (CATEGORIES, BIZ_ID)
		review = REVIEW_TEMPLATE % (LONG_TEXT, BIZ_ID)
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

		# Results should be the probability of that category being chosen.
		result = {CATEGORIES: 1}
		self.assertEqual(results[0], result)

	def test_review_category(self):
		"""Tests the category_mapper to make sure it is properly running"""
		business = BUSINESS_TEMPLATE % (CATEGORIES, BIZ_ID)
		review = REVIEW_TEMPLATE % (TEXT, BIZ_ID)

		job = CategoryPredictor()
		self.assertEqual(
			job.review_category_mapper(None, json.loads(review)).next(),
			(BIZ_ID, ('review', TEXT))
		)
		self.assertEqual(
			job.review_category_mapper(None, json.loads(business)).next(),
			(BIZ_ID, ('categories', [CATEGORIES]))
		)

	def test_categories_to_reviews(self):
		"""Tests add_categories_to_reviews to make sure it is properly running"""
		category = [('categories', [CATEGORIES]), ('review', TEXT)]

		job = CategoryPredictor()
		result = ('all', {CATEGORIES: 1})
		self.assertEqual(
			job.add_categories_to_reviews_reducer(BIZ_ID, category).next(),
			result
		)

	def test_tokenize_reviews(self):
		"""Tests tokenize_reviews_mapper to make sure it is properly running"""
		review = {CATEGORIES: 1}

		job = CategoryPredictor()
		result = ('all', {CATEGORIES: 1})
		self.assertEqual(
			job.tokenize_reviews_mapper('all', review).next(),
			result
		)


if __name__ == '__main__':
	unittest.main()
