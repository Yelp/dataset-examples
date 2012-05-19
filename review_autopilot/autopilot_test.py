from __future__ import with_statement
from autopilot import ReviewAutoPilot
from unittest import TestCase
from StringIO import StringIO
import unittest

class TestReviewAutoPilotCase(TestCase):
	
	def test_business_mapper(self):
		"""tests the individual mappers of ReviewAutoPilot
		"""
		job = ReviewAutoPilot()
		DATA = ({'type':'business', 'business_id': 128411, 'data':'Info here'}, {'type': 'review', 'business_id':128411, 'text': 'Hello!'})
		self.assertEqual(job.business_join_mapper(None, DATA[0]).next(), (128411,('business',DATA[0])))
		self.assertEqual(job.business_join_mapper(None,DATA[1]).next(), (128411,('review',DATA[1]['text'])))

	def test_single_full_run(self):
		"""Does a full run of autopilot, ReviewAutoPilot to make sure if
		mr_job is still correct with the newest revision. Uses small, static
		dataset possible on local, since a full run takes too long.
		"""
		#Random data to feed into the markov model. Tested once to get the result (if it runs, they should be equal).
		SINGLE_REVIEW = '{"type":"review", "text":"foo bar foo baz foo car foo daz foo foo foo foo foo foo foo foo foo foo foofoo yelp foo yar foo foo bar bar dar", "business_id":"Yelp"}\n'
		BUSINESS= '{"type":"business", "categories":"Company", "business_id":"Yelp"}\n'
		static_stdin = StringIO(SINGLE_REVIEW + BUSINESS)

		job = ReviewAutoPilot(['-r', 'inline', '--no-conf', '-'])
		job.sandbox(stdin=static_stdin)

		results = []
		with job.make_runner() as runner:
			runner.run()
			for line in runner.stream_output():
				key, value = job.parse_output_line(line)
				results.append(value)
		result = {'foo': 0.99009900990099009, '<end>': 0.0099009900990099011} #Normal output to compare
		self.assertEqual(results[0], result)

	def test_categories_reducer(self):
		"""Tests join_reviews_with_categories_reducer with null data and some static data.
		"""
		job = ReviewAutoPilot()
		VALUES = (('business', {'categories': 'Food'}), ('review', 'Some text here'))
		BUSINESS_ID= 'Yelp'
		self.assertEqual(job.join_reviews_with_categories_reducer(BUSINESS_ID, VALUES).next(), ('Food', 'Some text here'))


if __name__ == '__main__':
	unittest.main()
