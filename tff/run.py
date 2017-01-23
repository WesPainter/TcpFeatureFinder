import argparse
import configparser
import os
import shutil
import sys


from yapsy.PluginManager import PluginManager

from .tcp_flow import TcpFlow
from .database_builder import DatabaseController, TcpFlowDb
from .report_builder import ReportBuilder
from .helpers import get_list_from_config

class Driver:
    '''
    Supports the execution of TcpFeatureFinder

    Driver stores state such as path to feature files directory, the tcpflow out
    directory, the tff out directory, the configuration values, and a connection
    to the backing database.

    Driver provides methods for constructing tcpflow objects based for files, as
    well as executes the plugins against each tcp flow object.

    '''

    def __init__(self, db_path, ff_dir, tcpout_dir, output_dir):

        self.output_dir = os.path.abspath(output_dir)
        self.db_path = os.path.join(self.output_dir, db_path)
        self.ff_dir = os.path.abspath(ff_dir)
        self.tcpout_dir = os.path.abspath(tcpout_dir)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.tcpflow_outdir = os.path.join(output_dir, "tcpflows")
        if not os.path.exists(os.path.join(self.tcpflow_outdir)):
            os.makedirs(self.tcpflow_outdir)

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.plugin_manager = PluginManager()
        self.plugin_manager.setPluginPlaces(["plugins"])
        self.plugin_manager.collectPlugins()

        self.db_controller = DatabaseController(self.db_path)
        self.plugins = self.get_active_plugins()
        self.tcp_flows = self.build_tcp_flows()
        self.report_builder = ReportBuilder(self.config, self.db_controller, self.output_dir, self.tcp_flows)


    def build_tcp_flows(self):
        '''
        Constructs TcpFlow objects for each tcp flow in tcp_out directory.

        This method will parse the tcpflow output directory and build an
        object per tcpflow file.  Additionally, each tcp flow will be committed
        to the designated output database.

        '''
        
        tcp_flows = []

        for direntry in os.scandir(self.tcpout_dir):
            if 'report.xml' in direntry.name or not direntry.is_file():
                continue

            tcp_flow = TcpFlow(direntry.path)
            self.db_controller.add_tcp_flow_to_session(tcp_flow)
            tcp_flows.append(tcp_flow)

        self.db_controller.commit_session()

        return tcp_flows
        

    def get_active_plugins(self):
        '''
        Makes sure only plugins designated in config.ini are used.

        Returns:
            List of active plugin objects
        '''

        plugins = get_list_from_config(self.config, 'active_plugins', 'plugins')

        active_plugins = []

        for plugin in self.plugin_manager.getAllPlugins():
            if plugin.name in plugins:
                active_plugins.append(plugin)

        return active_plugins

    def run(self):
        '''
        Runs Tcp Feature Finder.

        First, each plugin will assemble its features, look for them in each tcp flow,
        and filter any that are found.  It will then commit the found features to the
        output database.  Then any custom plugin reports will be generated, then all
        standard reports.  Finally, flows with features present will be moved into the
        output folder along with generated reports.

        '''

        # for each plugin, build its features list and find them in each tcpflow
        for plugin in self.plugins:
            plugin = plugin.plugin_object   
            plugin.get_features(self.ff_dir)

            # search for the features in each tcp flow using plugin gathered lists
            # filter out the features based on plugin logic

            feature_type = plugin.feature_name

            for tcp_flow in self.tcp_flows:
                tcp_flow.find_features(feature_type, plugin.features)
                found_features = tcp_flow.get_found_features()[feature_type]
                filtered_features = plugin.filter_features(tcp_flow.path, found_features)

                for feature, locations in filtered_features.items():
                    for location in locations:
                        self.db_controller.add_feature_to_session(
                            tcp_flow.filename, feature_type, feature, location)

                self.db_controller.commit_session()

        for plugin in self.plugins:
            plugin = plugin.plugin_object
            plugin_report = plugin.generate_report(self.db_controller)

            if plugin_report is not None:
                self.report_builder.save_report(plugin.feature_type + '_report.txt', plugin_report)

        self.report_builder.generate_reports()

        for tcpflow in self.tcp_flows:
            if self.db_controller.get_feature_count_by_flow(tcpflow.filename) > 0:
                shutil.copyfile(tcpflow.path, os.path.join(self.tcpflow_outdir, tcpflow.filename))

def main(db_path='../tff.db', ff_dir='../features', tcpout_dir='../tcpflow_out',
        output_dir='../tff_out'):

    '''
    Main function to execute tff

    Arguments:
        db_path - string path to database location
        ff_dir - path to feature file base directory
        tcpout_dir - path to output folder for tcpflow
        output_dir - path to direcory in which to store tff output data
        
    '''

    driver = Driver(db_path, ff_dir, tcpout_dir, output_dir)
    driver.run()


