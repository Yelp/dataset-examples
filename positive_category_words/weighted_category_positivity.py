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

import re

from mrjob.job import MRJob

def avg_and_total(iterable):
	"""Compute the average over a numeric iterable."""
	items = 0
	total = 0.0

	for item in iterable:
		total += item
		items += 1

	return total / items, total

# Considerably lower than for the simple global script, since category
# data is much more sparse
MINIMUM_OCCURENCES = 50

# Require reviews from AT LEAST this many distinct businesses before
# we include a word (prevents very popular restaurant names from
# showing up in the list)
MINIMUM_BUSINESSES = 3

class WeightedPositiveWords(MRJob):
	"""Find the most positive words in the dataset."""

	# The input is the dataset - interpret each line as a single json
	# value (the key will be None)
	DEFAULT_INPUT_PROTOCOL = 'json_value'

	def review_category_mapper(self, _, data):
		"""Walk over reviews, emitting each word and its rating."""
		if data['type'] == 'review':
			yield data['business_id'], ('review', (data['text'], data['stars']))

		elif data['type'] == 'business':
			# skip businesses with no categories
			if data['categories']:
				yield data['business_id'], ('categories', data['categories'])

	def category_join_reducer(self, business_id, reviews_or_categories):
		"""Emit category-word combinations."""
		categories = None
		reviews = []

		for data_type, data in reviews_or_categories:
			if data_type == 'review':
				reviews.append(data)
			else:
				categories = data

		# no categories found, skip this
		if not categories:
			return

		for category in categories:
			for review_positivity in reviews:
				yield category, (business_id, review_positivity)

	def review_mapper(self, category, biz_review_positivity):
		biz_id, (review, positivity) = biz_review_positivity

		# normalize words by lowercasing and dropping non-alpha
		# characters
		norm = lambda word: re.sub('[^a-z]', '', word.lower())
		# only include a word once per-review (which de-emphasizes
		# proper nouns)
		words = set(norm(word) for word in review.split())

		for word in words:
			yield (category, word), (biz_id, positivity)

	def positivity_reducer(self, category_word, biz_positivities):
		category, word = category_word

		businesses = set()
		positivities = []
		for biz_id, positivity in biz_positivities:
			businesses.add(biz_id)
			positivities.append(positivity)

		# don't include words that only show up for a few businesses
		if len(businesses) < MINIMUM_BUSINESSES:
			return

		avg, total = avg_and_total(positivities)

		if total < MINIMUM_OCCURENCES:
			return

		yield int(avg * 100), (category, total, word)

	def steps(self):
		return [self.mr(), 
				self.mr(self.review_category_mapper, self.category_join_reducer),
				self.mr(self.review_mapper, self.positivity_reducer)]


if __name__ == "__main__":
	WeightedPositiveWords().run()
