from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol


class MRWordFrequencyCount(MRJob):

    # INPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, _, data):
        yield "longitudes", len(data)
        yield "latitudes", len(data.split())
        yield "lines", 1

    def reducer(self, key, values):
        yield key, sum(values)


if __name__ == '__main__':
    MRWordFrequencyCount.run()
