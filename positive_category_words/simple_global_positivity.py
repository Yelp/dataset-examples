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
from mrjob.protocol import JSONValueProtocol

MINIMUM_OCCURENCES = 1000

def avg_and_total(iterable):
    """Compute the average over a numeric iterable."""
    items = 0
    total = 0.0

    for item in iterable:
        total += item
        items += 1

    return total / items, total

class PositiveWords(MRJob):
    """Find the most positive words in the dataset."""

    # The input is the dataset - interpret each line as a single json
    # value (the key will be None)
    INPUT_PROTOCOL = JSONValueProtocol

    def review_mapper(self, _, data):
        """Walk over reviews, emitting each word and its rating."""
        if data['type'] != 'review':
            return

        # normalize words by lowercasing and dropping non-alpha
        # characters
        norm = lambda word: re.sub('[^a-z]', '', word.lower())
        # only include a word once per-review (which de-emphasizes
        # proper nouns)
        words = set(norm(word) for word in data['text'].split())

        for word in words:
            yield word, data['stars']

    def positivity_reducer(self, word, ratings):
        """Emit average star rating, word in a format we can easily
        sort with the unix sort command: 
        [star average * 100, total count], word.
        """
        avg, total = avg_and_total(ratings)

        if total < MINIMUM_OCCURENCES:
            return

        yield (int(avg * 100), total), word

    def steps(self):
        return [self.mr(), # Split apart the dataset into multiple
                # chunks. In regular hadoop-land you could change the
                # splitter. This is normally < 30 seconds of work.
                self.mr(self.review_mapper, self.positivity_reducer)]


if __name__ == "__main__":
    PositiveWords().run()
