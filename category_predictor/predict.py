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

"""Use the output from the CategoryPredictor MRJob to predict the
category of text. This uses a simple naive-bayes model - see
http://en.wikipedia.org/wiki/Naive_Bayes_classifier for more details.
"""

from __future__ import with_statement

import math
import sys

import category_predictor

class ReviewCategoryClassifier(object):
	"""Predict categories for text using a simple naive-bayes classifier."""

	@classmethod
	def load_data(cls, input_file):
		"""Read the output of the CategoryPredictor mrjob, returning
		total category counts (count of # of reviews for each
		category), and counts of words for each category.
		"""

		job = category_predictor.CategoryPredictor()

		category_counts = None
		word_counts = {}

		with open(input_file) as src:
			for line in src:
				category, counts = job.parse_output_line(line)

				if category == 'all':
					category_counts = counts
				else:
					word_counts[category] = counts

		return category_counts, word_counts

	@classmethod
	def normalize_counts(cls, counts):
		"""Convert a dictionary of counts into a log-probability
		distribution.
		"""
		total = sum(counts.itervalues())
		lg_total = math.log(total)

		return dict((key, math.log(cnt) - lg_total) for key, cnt in counts.iteritems())

	def __init__(self, input_file):
		"""input_file: the output of the CategoryPredictor job."""
		category_counts, word_counts = self.load_data(input_file)

		self.word_given_cat_prob = {}
		for cat, counts in word_counts.iteritems():
			self.word_given_cat_prob[cat] = self.normalize_counts(counts)

		# filter out categories which have no words
		seen_categories = set(word_counts)
		seen_category_counts = dict((cat, count) for cat, count in category_counts.iteritems() \
										if cat in seen_categories)
		self.category_prob = self.normalize_counts(seen_category_counts)

	def classify(self, text):
		"""Classify some text using the result of the
		CategoryPredictor MRJob. We use a basic naive-bayes model,
		eg, argmax_category p(category) * p(words | category) ==
		p(category) * pi_{i \in words} p(word_i | category).

		p(category) is stored in self.category_prob, p(word | category
		is in self.word_given_cat_prob.
		"""
		# start with prob(category)
		lg_scores = self.category_prob.copy()

		# then multiply in the individual word probabilities
		# NOTE: we're actually adding here, but that's because our
		# distributions are made up of log probabilities, which are
		# more accurate for small probabilities. See
		# http://en.wikipedia.org/wiki/Log_probability for more
		# details.
		for word in category_predictor.words(text):
			for cat in lg_scores:
				cat_probs = self.word_given_cat_prob[cat]

				if word in cat_probs:
					lg_scores[cat] += cat_probs[word]
				else:
					lg_scores[cat] += cat_probs['UNK']

		# convert scores to a non-log value
		scores = dict((cat, math.exp(score)) for cat, score in lg_scores.iteritems())

		# normalize the scores again - this isnt' strictly necessary,
		# but it's nice to report probabilities with our guesses
		total = sum(scores.itervalues())
		return dict((cat, prob / total) for cat, prob in scores.iteritems())


if __name__ == "__main__":
	input_file = sys.argv[1]
	text = sys.argv[2]

	guesses = ReviewCategoryClassifier(input_file).classify(text)

	best_guesses = sorted(guesses.iteritems(), key=lambda (_, prob): prob, reverse=True)[:5]

	for guess, prob in best_guesses:
		print 'Category: "%s" - %.2f%% chance' % (guess, prob * 100)
