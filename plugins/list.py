import os
import sys

from tff import plugin

class ListFeatureFilePlugin(plugin.AbstractPlugin):
    '''
    Reads features from a newline dileneated list.

    '''

    def __init__(self):
        super(ListFeatureFilePlugin, self).__init__()
        self.feature_name = 'list.txt'
        self.feature_file = 'list.txt'
        self.features = []

    def get_features(self, basedir):
        file_path = os.path.join(basedir, self.feature_file)

        with open(file_path) as f:
            for line in f.readlines():
                self.features.append(line.strip())

    def filter_features(self, tcpflow_path, found_features):
        return found_features

