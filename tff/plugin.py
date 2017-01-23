import os
import sys

from yapsy.IPlugin import IPlugin

class AbstractPlugin(IPlugin):
    '''
    Interface class for use in developing plugins.

    If you are developing a plugin for Tcp Feature Finder, inherit from this class
    and be sure to override the get_features and filter_features methods at the
    very least. See methods for additional documentation.

    '''

    def __init__(self):
        '''
        The feature name will be used to designate the "feature type" in the 
        output reports, as well as in the output database.  The features list
        will store the features to be searched for.

        '''

        super(AbstractPlugin, self).__init__()
        self.feature_name = ""
        self.features = []

    def get_features(self, basedir):
        '''
        Retreive list of features to be searched for.

        This method must be overridden in order for the plugin to function. Use 
        this method as a means to retreive a list of features, either from a file
        placed in the features dir at the base of the project or somewhere else.

        Arguments:
            basedir - Fully qualified path to features base drectory

        Returns:
            features - a list of strings to search for in TCP flows

        '''

        raise NotImplementedError("Plugin must implement get_features.  See AbstractPlugin.")

    def filter_features(self, tcpflow_path, found_features):
        '''
        Filter features found in a tcpflow

        This method may be overridden in order to provide a mechanism for filtering
        out undesired features.  If no filter is desired, there is no need to
        override this method.

        Arguments:
            tcpflow_path - 
            found_features - a dictionary of the following format:
                { specific_feature : [file_offset] }

        Returns:
            filtered_features - a dictionary of the same format as the found_features
                argument with file_offsets
        
        '''

        return found_features

    def generate_report(self, db_controller):
        '''
        Generate a custom report for a plugin.

        If you do not need a custom report, there is no need to override this method.

        By default, the report will be saved into tff as a separate file with the 
        file name formatted as (plugin name)_report.txt. This behavior can be avoided
        by returning None at the end of the method and adding a custom report saving
        method within this function.

        Arguments:
            db_controller - an instance of the DatabaseController object for 
                querying the database to get useful information

        '''

        return None

