# Copyright 2011 Yelp and Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Gather the data necessary to generate reviews using a simple markov
model (see http://en.wikipedia.org/wiki/Markov_chain for more
details). We gather word-next word counts for each category,
eliminating rare pairs.
"""

import re

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

# Chance that the review will end after any given word.
END_OF_REVIEW_RATE = 0.01

MINIMUM_PAIR_COUNT = 5
MINIMUM_FOLLOW_PERCENTAGE = 0.01

def words(text):
    """An iterator over tokens (words) in text. Replace this with a
    stemmer or other smarter logic.
    """

    for word in text.split():
        # normalize words by lowercasing and dropping non-alpha
        # characters
        normed = re.sub('[^a-z]', '', word.lower())

        if not normed:
            continue

        yield normed

def word_pairs(text):
    """Given some text, yield out pairs of words (eg bigrams)."""
    last_word = None

    for word in words(text):
        if last_word is not None:
            yield last_word, word
        last_word = word

    yield last_word, "<end>"

class ReviewAutoPilot(MRJob):
    """Very simple markov model for reviews, parameterized on business category."""

    INPUT_PROTOCOL = JSONValueProtocol

    def business_join_mapper(self, _, data):
        """Walk through reviews and businesses, yielding out the raw
        data.
        """
        if data['type'] == 'business':
            yield data['business_id'], ('business', data)
        elif data['type'] == 'review':
            yield data['business_id'], ('review', data['text'])

    def join_reviews_with_categories_reducer(self, business_id, reviews_or_biz):
        """Join reviews with the categories from the associated
        business.
        """
        categories = None
        reviews = []

        for data_type, data in reviews_or_biz:
            if data_type == 'business':
                categories = data['categories']
            else:
                reviews.append(data)

        # don't bother with these businesses
        if not categories:
            return

        for review in reviews:
            yield categories, review

    def review_split_mapper(self, categories, review):
        """Split a review into pairs of words and yield out 
        (start word, category), (follow word, count), combining
        repeated pairs into a single emission.
        """
        pair_counts = {}

        for pair in word_pairs(review):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

        for (start, follow), count in pair_counts.iteritems():
            for category in categories:
                yield (start, category), (follow, count)

    def follow_probs_reducer(self, start_word_category, follow_word_counts):
        """Given a start word and a category, find the distribution
        over next words. When normalized, this count defines the
        transition probability for the markov chain.
        """
        start, category = start_word_category
        follow_counts = {}

        for follow_word, count in follow_word_counts:
            follow_counts[follow_word] = follow_counts.get(follow_word, 0) + count

        total_transitions = float(sum(follow_counts.itervalues()))

        include_word = lambda count: count > MINIMUM_PAIR_COUNT and count / total_transitions > MINIMUM_FOLLOW_PERCENTAGE
        thresholded_follow_counts = dict((word, count) for word, count in follow_counts.iteritems() if include_word(count))

        # filter out transitions where the transition has either
        # occurred a minimum number of times, or does not make up a
        # minimum percentage of outgoing transitions.
        if not thresholded_follow_counts:
            return

        # put a small weight on <end>, which means 'end of review'.
        thresholded_follow_counts['<end>'] = thresholded_follow_counts.get('<end>', 0.0) 
        thresholded_follow_counts['<end>'] += END_OF_REVIEW_RATE * float(sum(thresholded_follow_counts.itervalues()))

        # re-normalize the remaining transition weights.
        new_total = float(sum(thresholded_follow_counts.itervalues()))
        percentages = dict((follow, count / new_total) for follow, count in thresholded_follow_counts.iteritems())

        yield (category, start), percentages

    def steps(self):
        return [ self.mr(mapper=self.business_join_mapper, reducer=self.join_reviews_with_categories_reducer),
                self.mr(mapper=self.review_split_mapper, reducer=self.follow_probs_reducer)]

if __name__ == "__main__":
    ReviewAutoPilot().run()

