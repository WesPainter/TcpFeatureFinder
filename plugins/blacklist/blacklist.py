import os
import sys
import urllib.request

from plugins import list as list_plugin

class BlacklistFeaturePlugin(list_plugin.ListFeatureFilePlugin):
    '''
    Downloads malware blacklist and uses the domains as features.

    Blacklist courtesy of http://www.dshield.org/ipsascii.html.

    '''

    def __init__(self):
        super(BlacklistFeaturePlugin, self).__init__()
        self.feature_name = 'malware_blacklist'
        self.feature_file = self.pull_feature_file()
        self.features = []

    def pull_feature_file(self):
        file_name = 'blacklist.txt'
        site = 'http://www.dshield.org/ipsascii.html?limit=1000'
        response = urllib.request.urlopen(site).read().decode()

        with open(os.path.join('features',file_name), 'w') as f:
            for line in response.split('\n'):

                # ignore index error, means row won't have a feature
                try:
                    if line[0] == '#':
                        continue
                except IndexError as e:
                    continue

                line = line.split('\t')
                f.write("{}\n".format(line[0]))
            
        return file_name

    def get_features(self, basedir):
        super(BlacklistFeaturePlugin, self).get_features(basedir)

        for feature in self.features:
            if not feature:
                self.features.remove(feature)

    def filter_features(self, tcpflow_path, found_features):
        return found_features

