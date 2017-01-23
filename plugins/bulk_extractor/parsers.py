import os
import sys

class BulkExtractorFileParser:

    def __init__(self, basedir):
        self.basedir = basedir

    def __check_valid_file(self, file_path):
        try:
            if os.path.getsize(file_path) == 0:
                print(os.path.getsize(file_path))
                return False
        except OSError as e:
            print('[-] Feature file {} does not exist.'.format(file_path))
            return False

        return True

    def parse_all_features(self):
        features = []
        features += self.parse_email_features()
        features += self.parse_ccn_features()
        features += self.parse_domain_features()
        features += self.parse_url_searches()

        out_features = []

        for feature in features:
            if len(feature) <=3:
                continue
            out_features.append(feature)

        return out_features
        
    def parse_email_features(self):
        path = os.path.join(self.basedir, 'email.txt')
        features = []
        
        if not self.__check_valid_file(path):
            return features

        with open(path, 'r') as f:
            f.readline()

            for line in f.readlines():

                if line[0] == '#':
                    continue

                line = line.split()
                feature = line[1].replace('\\x00','')

                if feature not in features:
                    features.append(feature)

        return features

    def parse_ccn_features(self):
        path = os.path.join(self.basedir, 'ccn_histogram.txt')
        features = []

        if not self.__check_valid_file(path):
            return features

        with open(path, 'r') as f:
            f.readline()

            for line in f.readlines():

                if line[0] == '#':
                    continue

                line = line.split()
                feature = line[1]

        return features

#    def parse_telephone_features(self):
#        path = os.path.join(self.basedir, 'telephone_histogram.txt')
#        features = []
#s
#        return features

    def parse_domain_features(self):
        path = os.path.join(self.basedir, 'domain_histogram.txt')
        features = []

        if not self.__check_valid_file(path):
            return features

        with open(path, 'r') as f:
            f.readline()

            for line in f.readlines():

                if line[0] == '#':
                    continue

                line = line.split()
                feature = line[1]

        return features

    def parse_url_searches(self):
        path = os.path.join(self.basedir, 'url_searches.txt')
        features = []

        if not self.__check_valid_file(path):
            return features

        with open(path, 'r') as f:

            last_line = f.readline()

            for line in f.readlines():

                if line[0] == '#':
                    continue

                line = line.split()
                feature = line[1]

                if feature in last_line or len(feature) <= 3:
                    last_line = line
                    continue

                if feature not in features:
                    features.append(feature)

                last_line = line

        return features


