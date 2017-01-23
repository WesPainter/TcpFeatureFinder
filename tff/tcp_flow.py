import os
import sys

class TcpFlow:
    '''
    Object to search a given tcp flow for a list of features.

    Stores information about the flow as well as searches for features and stores
    any found features with 

    '''

    def __init__(self, path):
        self.path = path
        self.search_features = []
        self.found_features = {}
        self.__parse_file_name()

    def __parse_file_name(self):
        '''
        Parse the filename for information about the tcp flow

        '''

        self.filename = os.path.basename(self.path)
        working = self.filename

        # Extract timestamp, if present
        if "T" in working:
            split = working.split("T")
            self.timestamp = split[0]
            working = split[1]
        else:
            self.timestamp = None

        # Extract connection number, if present
        if "c" in working:
            split = working.split("c")
            self.connection_number = split[1] 
            working = split[0]
        else:
            self.connection_number = 0

        # Extract VLAN if present
        if "--" in working:
            split = working.split("--")
            self.vlan = split[1]
            working = split[0]
        else:
            self.vlan = None
            
        splits = working.split('-')
        source = splits[0].rsplit('.', 1)
        dest = splits[1].rsplit('.', 1)

        self.source_ip = source[0]
        self.source_port = source[1]
        self.dest_ip = dest[0]
        self.dest_port = dest[1]

    def find_features(self, feature_type, search_features):
        '''
        Search for designated features within the tcp flow file and save the 
        position of the line containg that feature in found_features

        '''

        found = {}

        with open(self.path, 'r') as f:
            while(True):
                try:
                    position = f.tell()
                    line = f.readline()
                except UnicodeDecodeError as e:
                    continue
                if not line:
                    break

                for feature in search_features:
                    if feature in line:
                        if feature not in found:
                            found[feature] = []
                        found[feature].append(position)

        self.found_features[feature_type] = found

    def get_found_features(self):
        return self.found_features
