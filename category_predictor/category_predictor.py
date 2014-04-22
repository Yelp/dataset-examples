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

"""An MRJob that constructs the data necessary to predict category
information
"""

import re

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

# require at least this many occurences for a word to show up for a
# given category 
MINIMUM_OCCURENCES = 100

def words(text):
    """An iterator over tokens (words) in text. Replace this with a
    stemmer or other smarter logic.
    """

    for word in text.split():
        # normalize words by lowercasing and dropping non-alpha
        # characters
        normed = re.sub('[^a-z]', '', word.lower())

        if normed:
            yield normed

class CategoryPredictor(MRJob):
    """A very simple category predictor. Trains on review data and
    generates a simple naive-bayes model that can predict the category
    of some text.
    """

    # The input is the dataset - interpret each line as a single json
    # value (the key will be None)
    INPUT_PROTOCOL = JSONValueProtocol

    def review_category_mapper(self, _, data):
        """Visit reviews and businesses, yielding out (business_id,
        (review or category)).
        """
        if data['type'] == 'review':
            yield data['business_id'], ('review', data['text'])
        elif data['type'] == 'business':
            yield data['business_id'], ('categories', data['categories'])

    def add_categories_to_reviews_reducer(self, business_id, reviews_or_categories):
        """Yield out (category, review) for each category-review
        pair. We'll do the actual review tokenizing in the next
        mapper, since you typically have much more map-capacity than
        reduce-capacity.
        """
        categories = None
        reviews = []

        for data_type, data in reviews_or_categories:
            if data_type == 'review':
                reviews.append(data)
            else:
                categories = data

        # We either didn't find a matching business, or this biz
        # doesn't have any categories. In either case, we can drop
        # these reviews.
        if not categories:
            return

        # Yield out review counts in the same format as the
        # tokenize_reviews_mapper. We'll special case the 'all' key in
        # that method, but afterwards it will be treated the same.
        yield 'all', dict((cat, len(reviews)) for cat in categories)

        for category in categories:
            for review in reviews:
                yield category, review

    def tokenize_reviews_mapper(self, category, review):
        """Split reviews into words, yielding out (category, {word: count}) and
        ('all', {word: count}). We yield out a dictionary of counts
        rather than a single entry per-word to reduce the amount of
        i/o between mapper and reducer.
        """
        # special case - pass through category counts (which are
        # already formatted like the output of this mapper)
        if category == 'all':
            yield category, review
            return

        counts = {}
        for word in words(review):
            counts[word] = counts.get(word, 0) + 1

        yield category, counts

    def sum_counts(self, category, counts):
        """Sum up dictionaries of counts, filter out rare words
        (bucketing them into an unknown word bucket), and yield the
        counts.
        """
        raw_count = {}

        # sum up the individual counts
        for word_count in counts:
            for word, count in word_count.iteritems():
                raw_count[word] = raw_count.get(word, 0) + count

        # don't filter out low-mass categories
        if category == 'all':
            yield category, raw_count
            return

        # filter out low-count words; assign a very low mass to
        # unknown words
        filtered_counts = {}
        for word, count in raw_count.iteritems():
            if count > MINIMUM_OCCURENCES:
                filtered_counts[word] = count

        # don't include categories with every word filtered out
        if not filtered_counts:
            return

        # Assign a small mass to unknown tokens - check out
        # http://en.wikipedia.org/wiki/Laplacian_smoothing for background.
        filtered_counts['UNK'] = 0.01

        # emit the result
        yield category, filtered_counts

    def steps(self):
        return [self.mr(mapper=self.review_category_mapper, 
                reducer=self.add_categories_to_reviews_reducer),
            self.mr(mapper=self.tokenize_reviews_mapper, 
                reducer=self.sum_counts)] 


if __name__ == "__main__":
    CategoryPredictor().run()

