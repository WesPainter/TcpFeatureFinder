import os
import sys

from tff import plugin

from plugins.bulk_extractor.parsers import BulkExtractorFileParser

class BulkExtractorPlugin(plugin.AbstractPlugin):
    '''
    bulk_extractor output plugin for TcpFeatureFlow

    '''

    def __init__(self):
        super(BulkExtractorPlugin, self).__init__()
        self.feature_name = 'bulk_extractor'

    def get_features(self, basedir):
        file_path = os.path.join(basedir, 'bulk_out')
        self.parser = BulkExtractorFileParser(file_path)
        self.features = self.parser.parse_all_features()


    def filter_features(self, tcpflow_path, found_features):
        if not found_features:
            return found_features

        with open(tcpflow_path, 'r') as f:
            for feature, positions in found_features.items():
                for position in positions:
                    f.seek(int(position))

                    try:
                        f.readline()
                    except UnicodeDecodeError as e:
                        continue
                
        return found_features
