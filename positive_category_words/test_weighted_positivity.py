from __future__ import with_statement
from unittest import TestCase
from StringIO import StringIO
import unittest
import json

from weighted_category_positivity import WeightedPositiveWords


COMPANY='Company'
REVIEW_TEMPLATE = '{"type":"review", "stars":3, "text":"%s", "business_id":"%s"}\n'
BUSINESS_TEMPLATE = '{"type":"business", "categories":["'+ COMPANY +'"], "business_id":"%s"}\n'		
TEXT = "Hello world"
BIZ_NAME = 'Qdoba' 


class TestWeightedPositiveWords(TestCase):
	
	def test_smoke(self):
		"""Does a full run of weighted positive words"""
		
		# Need 3 mock businesses to test
		business1 = BUSINESS_TEMPLATE % "Yelp"
		business2 = BUSINESS_TEMPLATE % "Target"
		business3 = BUSINESS_TEMPLATE % "Walmart"

		# Need more than 1 review for weighted threshold
		review1 = REVIEW_TEMPLATE % (TEXT, "Yelp")
		review2 = REVIEW_TEMPLATE % (TEXT, "Target")
		review3 = REVIEW_TEMPLATE % (TEXT, "Walmart")		

		# Need at least 50 occurrences of reviews, so multiply the first review by 20
		total_input = business1 + business2 + business3 + (review1 * 20) + review2 + review3
		static_stdin = StringIO(total_input)

		job = WeightedPositiveWords(['-r', 'inline', '--no-conf', '-'])
		job.sandbox(stdin=static_stdin)

		results = []
		with job.make_runner() as runner:
			runner.run()
			for line in runner.stream_output():
				key, value = job.parse_output_line(line)
				results.append(value)
		result = [COMPANY, 66.0, 'hello'] 
		self.assertEqual(results[0], result)
	
	def test_review_category(self):
		"""Test the review_category_mapper function with a mock input"""
		review = REVIEW_TEMPLATE % ("Awesome dinner place", "Qdoba")
		business = BUSINESS_TEMPLATE % BIZ_NAME

		job = WeightedPositiveWords()
		results = (u'Qdoba', ('review', (u'Awesome dinner place', 3))), (u'Qdoba', ('categories', [u'Company'])) 
		self.assertEqual(job.review_category_mapper(None, json.loads(review)).next(), results[0])
		self.assertEqual(job.review_category_mapper(None, json.loads(business)).next(), results[1])

	def test_category_join(self):
		"""Test the category_join_reducer function with the same results
		from above. These tests should be used to isolate where an error
		will come from if a person changes any of the functions in the mr
		"""
		review_or_categories = (('review', ('Awesome dinner place', 3)),  ('categories', [COMPANY])) 
		
		job = WeightedPositiveWords()
		results = (COMPANY, (BIZ_NAME, ('Awesome dinner place', 3)))
		self.assertEqual(job.category_join_reducer(BIZ_NAME, review_or_categories).next(), results)
	
	def test_review_mapper(self):
		"""Test the review_mapper function to make sure that based on a mock input,
		it produces the correct calculated output
		"""
		biz_review_positivity =  (BIZ_NAME, ('Awesome dinner place', 3))

		job = WeightedPositiveWords()
		results = ((COMPANY, 'awesome'), (BIZ_NAME, 3))
		self.assertEqual(job.review_mapper(COMPANY, biz_review_positivity).next(), results)
	
if __name__ == '__main__':
	unittest.main()
