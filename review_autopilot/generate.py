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

from __future__ import with_statement

import random
import sys

import autopilot

class ReviewMarkovGenerator(object):
    """Generate the remainder of a review, given a category and some
    start text.
    """
    
    @classmethod
    def load_data(cls, input_file):
        """Read the output of the ReviewAutoPilot mrjob, returning a
        transition distribution. The transition distribution is a
        dictionary with category keys. Each category key points to
        another dictionary, which contains word keys, which contain
        another set of dictionaries, which contain the probability of
        transitioning to the the next word.

        Here's an example:

        category_transitions = {'Food': {'hot': {'dog': 1.0}}}

        This means that for the category Food, the word 'hot' has a
        100% probability of being followed by the word 'dog'.
        """
        job = autopilot.ReviewAutoPilot()

        category_transitions = {}

        with open(input_file) as src:
            for line in src:
                (category, start), transitions = job.parse_output_line(line)

                category_transitions.setdefault(category, {})[start] = transitions

        return category_transitions

    @classmethod
    def sample(cls, distribution):
        """Sample from a dictionary containing a probability
        distribution.
        """
        guess = random.random()

        for word, prob in distribution.iteritems():
            if guess <= prob:
                return word

            guess -= prob

        # random.random() returns a value between 0 and 1. The values
        # of distribution are assumed to sum to 1 (since distribution
        # is a probability distribution), so random.random() -
        # sum(values) == 0. If this is not the case, then distribution
        # is not a valid distribution.
        assert False, "distribution is not a valid probability distribution!"

    def __init__(self, input_file):
        """input_file: the output of the ReviewAutopilot job."""
        self.category_transitions = self.load_data(input_file)

    def complete(self, category, text):
        """Complete some text."""
        if category not in self.category_transitions:
            raise KeyError('Unknown category (invalid or not enough data): %s' % category)

        words = list(autopilot.words(text))

        last_word = words[-1]
        transitions = self.category_transitions[category]
        while True:
            next_word = self.sample(transitions[last_word])

            # the end-of-review token is None, which is JSON null,
            # which is coerced to the string "null" (since json
            # objects can only have strings as keys)
            if next_word == "<end>":
                break

            text += ' ' + next_word
            last_word = next_word

        return text


if __name__ == "__main__":
    input_file = sys.argv[1]
    category = sys.argv[2]
    text = sys.argv[3]

    print ReviewMarkovGenerator(input_file).complete(category, text)
