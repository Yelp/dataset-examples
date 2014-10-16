# -*- coding: utf-8 -*-
"""Test the json to csv converter script."""
from unittest2 import TestCase

import json_to_csv_converter


class TestJsonToCsvConverter(TestCase):

    """Test the json to csv converter script."""

    test_biz = {
        'type':'business',
        'business_id': 123,
        'hours': {
            'Monday': {
                'open': "11:30",
                'close': "21:00",
                },
            },
        }
    test_biz_column_names = frozenset(['type', 'business_id', 'hours.Monday.open', 'hours.Monday.close'])
    test_review = {
        'type': 'review',
        'user_id': 345,
        'votes': {
            'funny': 1,
            },
        }
    test_review_column_names = frozenset(['type', 'user_id', 'votes.funny'])

    def test_get_column_names(self):
        """Test that we see the expected column names for the test objects."""
        biz_column_names = set(json_to_csv_converter.get_column_names(self.test_biz))
        self.assertEqual(biz_column_names, self.test_biz_column_names)

        review_column_names = set(json_to_csv_converter.get_column_names(self.test_review))
        self.assertEqual(review_column_names, self.test_review_column_names)

    def test_get_nested_value(self):
        """Test getting a nested value from a dict given a flat key."""
        # non-nested values
        self.assertEqual(
                json_to_csv_converter.get_nested_value(self.test_review, 'type'),
                'review'
                )
        # nested values
        self.assertEqual(
                json_to_csv_converter.get_nested_value(self.test_biz, 'hours.Monday.open'),
                '11:30'
                )
        # unknown values
        self.assertIsNone(
                json_to_csv_converter.get_nested_value(self.test_review, 'this.is.not.in.the.review'),
                )

