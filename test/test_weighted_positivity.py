from __future__ import with_statement

import json
import unittest
from unittest import TestCase
from StringIO import StringIO
import testify as T

from positive_category_words.weighted_category_positivity import WeightedPositiveWords


CATEGORY = u'Company'
REVIEW_TEMPLATE = ('{"type":"review", "stars":3, "text":"%s",'
'"business_id":"%s"}\n')
BUSINESS_TEMPLATE = ('{"type":"business", "categories":["%s"], '
'"business_id":"%s"}\n')
TEXT = u"Hello world"
BIZ_NAME = u'Qdoba'


class TestWeightedPositiveWords(TestCase):

    def test_smoke(self):
        """Does a full run of weighted positive words"""

        # Need 3 mock businesses to test
        business1 = BUSINESS_TEMPLATE % (CATEGORY, "Yelp")
        business2 = BUSINESS_TEMPLATE % (CATEGORY, "Target")
        business3 = BUSINESS_TEMPLATE % (CATEGORY, "Walmart") 
        # Need more than 1 review for weighted threshold
        review1 = REVIEW_TEMPLATE % (TEXT, "Yelp")
        review2 = REVIEW_TEMPLATE % (TEXT, "Target")
        review3 = REVIEW_TEMPLATE % (TEXT, "Walmart")

        # Need at least 50 occurrences of reviews, so multiply the first review by 20
        total_input = (business1 + business2 + business3
            + (review1 * 20) + review2 + review3)
        static_stdin = StringIO(total_input)

        job = WeightedPositiveWords(['-r', 'inline', '--no-conf', '-'])
        job.sandbox(stdin=static_stdin)

        results = []
        with job.make_runner() as runner:
            runner.run()
            for line in runner.stream_output():
                key, value = job.parse_output_line(line)
                results.append(value)
        end_result = [[CATEGORY, 66.0, 'hello'], [CATEGORY, 66.0, 'world']]
        self.assertEqual(results, end_result)

    def test_review_category(self):
        """Test the review_category_mapper function with a mock input"""

        review = REVIEW_TEMPLATE % (TEXT, BIZ_NAME)
        business = BUSINESS_TEMPLATE % (CATEGORY, BIZ_NAME)

        job = WeightedPositiveWords()
        review_results = list(job.review_category_mapper(None, json.loads(review)))
        biz_results = list(job.review_category_mapper(None, json.loads(business)))
        review_after_results = [(BIZ_NAME, ('review', (TEXT, 3)))]                
        biz_after_results = [(BIZ_NAME, ('categories', [CATEGORY]))]
        self.assertEqual(review_results, review_after_results)
        self.assertEqual(biz_results, biz_after_results)


    def test_category_join(self):
        """Test the category_join_reducer function with the same results
        from above. These tests should be used to isolate where an error
        will come from if a person changes any of the functions in the mr
        """
        review_or_categories = (('review', (TEXT, 3)),  ('categories', [CATEGORY]))

        job = WeightedPositiveWords()
        join_results = list(job.category_join_reducer(BIZ_NAME, review_or_categories))
        results = [(CATEGORY, (BIZ_NAME, (TEXT, 3)))]
        self.assertEqual(join_results, results)

    def test_review_mapper(self):
        """Test the review_mapper function to make sure that based on a mock input,
        it produces the correct calculated output
        """
        biz_review_positivity = (BIZ_NAME, (TEXT, 3))

        job = WeightedPositiveWords()
        review_results = list(job.review_mapper(CATEGORY, biz_review_positivity))
        results = [((CATEGORY, u'world'), (BIZ_NAME, 3)), ((CATEGORY, u'hello'), (BIZ_NAME, 3))]
        T.assert_sorted_equal(review_results, results)

if __name__ == '__main__':
    unittest.main()
