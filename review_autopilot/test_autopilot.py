from __future__ import with_statement
from unittest import TestCase
from StringIO import StringIO
import unittest

from autopilot import ReviewAutoPilot

# These are used to create stdin string data.
CATEGORIES = 'Company'
REVIEW_TEMPLATE = '{"type":"review", "stars":3, "text":"%s",\
"business_id":"%s"}\n'
BUSINESS_TEMPLATE = '{"type":"business", "categories": "%s",\
"business_id":"%s"}\n'
TEXT = 'Hello!'
BIZ = 'Yelp'
# This is used to pass around dict data, which is slightly different than
# the string data above.
DATA = [
	{'type':'business', 'business_id': 128411, 'data':'Info here'},
	{'type': 'review', 'business_id':128411, 'text': TEXT}
]


class TestReviewAutoPilotCase(TestCase):

	def test_business_mapper(self):
		"""tests the individual mappers of ReviewAutoPilot"""
		job = ReviewAutoPilot()

		self.assertEqual(job.business_join_mapper(None, DATA[0]).next(),
			(128411, ('business', DATA[0])))
		self.assertEqual(job.business_join_mapper(None, DATA[1]).next(),
		(128411, ('review', DATA[1]['text'])))

	def test_smoke(self):
		"""Uses small, static dataset possible on local, since a full run takes
		too long."""
		#Random data to feed into the markov model.
		#I use long runs of foo to get through the threshold filters.
		text = '"foo bar foo baz foo car foo daz' + 'foo' * 10 + 'foofoo yelp \
foo yar foo foo bar bar dar"'

		single_review = REVIEW_TEMPLATE % (text, BIZ)
		business = BUSINESS_TEMPLATE % (CATEGORIES, BIZ)
		static_stdin = StringIO(single_review + business)

		job = ReviewAutoPilot(['-r', 'inline', '--no-conf', '-'])
		job.sandbox(stdin=static_stdin)

		results = []
		with job.make_runner() as runner:
			runner.run()
			for line in runner.stream_output():
				key, value = job.parse_output_line(line)
				results.append(value)

		# Normal output to compare
		result = {'foo': 0.99009900990099009, '<end>': 0.0099009900990099011}
		self.assertEqual(results[0], result)

	def test_categories_reducer(self):
		"""Tests join_reviews_with_categories_reducer with null data and some
		static data."""
		job = ReviewAutoPilot()
		VALUES = (('business', {'categories': CATEGORIES}), ('review', TEXT))
		self.assertEqual(job.join_reviews_with_categories_reducer(BIZ,
																VALUES).next(),
						(CATEGORIES, TEXT))

	def test_split_mapper(self):
		"""Tests split_mapper reducer in autopilot"""
		job = ReviewAutoPilot()
		TEST_RETURN = (('is', 'F'), ('a', 1))
		self.assertEqual(job.review_split_mapper(CATEGORIES, TEXT).next(),
			TEST_RETURN)


if __name__ == '__main__':
	unittest.main()
