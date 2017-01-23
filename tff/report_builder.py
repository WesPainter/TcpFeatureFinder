import collections
import operator
import os
import sys

from .tcp_flow import TcpFlow
from .helpers import get_list_from_config

class ReportBuilder:
    '''
    Object used to build reports.

    Arguments:
        config - copy of the config object
        db_controller - instance of DatabaseController for database manipulation
        outdir - path to tff output directory
        tcpflows - path to tcp flows

    '''

    def __init__(self, config, db_controller, outdir, tcpflows):
        self.config = config
        self.db_controller = db_controller
        self.outdir = outdir
        self.tcpflows = tcpflows
        self.report_header = "# TcpFeatureFinder v1.0\n"  

    def generate_reports(self):
        '''
        Main function generates all reports activated in config.ini

        '''

        self.ips = self.db_controller.get_all_ips()
        reports = get_list_from_config(self.config, 'reports', 'reports')

        if 'feature_type_hist' in reports:
            self.gen_feature_type_hist()
        if 'ip_hist' in reports:
            self.gen_ip_hist()
        if 'ip_report' in reports:
            for ip in self.ips:
                self.gen_ip_report(ip)
        if 'tcpflow_report' in reports:
            for tcpflow in self.tcpflows:
                if self.db_controller.get_feature_count_by_flow(tcpflow.filename) > 0:
                    self.gen_tcpflow_report(tcpflow)


    def gen_feature_type_hist(self):
        feature_type_list = self.db_controller.count_feature_type()
        report = self.report_header
        report += "# Feature Type Histogram\n\n"

        rank = 0
        for (count, feature_type) in feature_type_list:
            rank += 1
            report += "{}.\t{}\t{}".format(rank, feature_type, count)

        self.save_report('featuretype_histogram.txt', report)

    def gen_ip_hist(self):
        '''
        Builds a report containing features found for each ip address and saves
        it to the output folder.

        '''
        report = self.report_header
        report += "# IP Histogram of Found Features\n\n"

        ip_list = self.db_controller.count_num_features_by_ip()
        src_ip_list = ip_list[0]
        dest_ip_list = ip_list[1]

        total_list = {}

        for (count, ip) in src_ip_list + dest_ip_list:
            if ip not in total_list:
                total_list[ip] = count
            else:
                total_list[ip] += count

        sorted_ips = sorted(total_list.items(), key=operator.itemgetter(1), reverse=True)

        rank = 0
        for (ip, count) in sorted_ips:
            rank += 1
            report += "{}.\t{}\t{}\n".format(rank, ip, count)
        
        self.save_report('ip_histogram.txt', report)

    def gen_ip_report(self, ip):
        '''
        Builds a report for each individual IP address that has at least one
        associated feature.

        '''

        if not os.path.exists(os.path.join(self.outdir, 'ip_reports')):
            os.makedirs(os.path.join(self.outdir, 'ip_reports'))

        paired_ips = self.db_controller.get_paired_ips(ip)
        sorted_paired_ips = sorted(
            paired_ips.items(), key=operator.itemgetter(1), reverse=True)

        src_features, dest_features = self.db_controller.get_features_by_ip(ip)
        src_ft, dest_ft = self.db_controller.get_feature_types_by_ip(ip)
        features = src_features + dest_features

        feature_counts = {}
        src_feature_counts = {}
        dest_feature_counts = {}

        for feature in set(features):
            feature_counts[feature] = features.count(feature)

        for feature in set(src_features):
            src_feature_counts[feature] = src_features.count(feature)

        for feature in set(dest_features):
            dest_feature_counts[feature] = dest_features.count(feature)

        sorted_features = sorted(
            feature_counts.items(), key=operator.itemgetter(1), reverse=True)
        src_sorted_features = sorted(
            src_feature_counts.items(), key=operator.itemgetter(1), reverse=True)
        dest_sorted_features = sorted(
            dest_feature_counts.items(), key=operator.itemgetter(1), reverse=True)

        report = self.report_header
        report += "# {} Feature Report\n\n".format(ip)

        report += "Unique Features Found: {}\n".format(len(set(features)))
        report += "Features Found: {}\n".format(len(src_features) + len(dest_features))
        report += "Feature Types Found: {}\n\n".format(len(src_ft) + len(dest_ft))

        report += "All Found Features Histogram\n"
        report += "Rank\tFeature\tCount\n"

        rank = 0
        for (feature, count) in sorted_features:
            rank += 1
            report += "{}.\t{}\t{}\n".format(rank, feature, count)

        report += "\n"
        report += "Src Found Features Histogram\n"
        report += "Rank\tFeature\tCount\n"
 
        rank = 0
        for (feature, count) in src_sorted_features:
            rank += 1
            report += "{}.\t{}\t{}\n".format(rank, feature, count)

        report += "\n"
        report += "Dest Found Features Histogram\n"
        report += "Rank\tFeature\tCount\n"

        rank = 0
        for (feature, count) in dest_sorted_features:
            rank += 1
            report += "{}.\t{}\t{}\n".format(rank, feature, count)

        report += "\n"
        report += "IP interaction histogram by number of features found\n"
        report += "Rank\tIP\tCount\n"

        rank = 0
        for (paired_ip, count) in sorted_paired_ips:
            rank += 1
            report += "{}.\t{}\t{}\n".format(rank, paired_ip, count)

        self.save_report(os.path.join('ip_reports', ip + '_report.txt'), report)

    def gen_tcpflow_report(self, tcpflow):
        '''
        Builds a report for each tcp flow with associated features and writes it
        to the output directory.

        '''

        if not os.path.exists(os.path.join(self.outdir, 'tcpflow_reports')):
            os.makedirs(os.path.join(self.outdir, 'tcpflow_reports'))

        feature_types = self.db_controller.get_feature_types_by_flow(tcpflow.filename)
        features = self.db_controller.get_features_by_flow(tcpflow.filename)

        features_count = {}
        for feature in features:
            if feature[0] not in features_count:
                features_count[feature[0]] = 1
            else:
                features_count[feature[0]] += 1

        sorted_feature_count = sorted(
            features_count.items(), key=operator.itemgetter(1), reverse=True)

        report = self.report_header
        report += "# {} TcpFlow Report\n\n".format(tcpflow.filename)

        report += "Source: {}\n".format(tcpflow.source_ip)
        report += "Destination: {}\n".format(tcpflow.dest_ip)
        report += "Total Features Found: {}\n".format(len(features))
        report += "Total Feature Types Found: {}\n\n".format(len(feature_types))

        report += "Feature Types Found\n"
        for feature_type in feature_types:
            report += "{}\n".format(feature_type[0])

        report += "\n"
        report += "Features Found\n"
        rank = 0
        for (feature, count) in sorted_feature_count:
            rank += 1
            report += "{}.\t{}\t{}\n".format(rank, feature, count)
        
        self.save_report(os.path.join('tcpflow_reports', tcpflow.filename + '_report.txt'), report)

    def save_report(self, filename, report):
        '''
        Save a report with the given filename to the output directory.

        Arguments:
            filename - String name of file
            report - report string to save into file

        '''
            
        path = os.path.join(self.outdir, filename)
        with open(path, 'w') as f:
            f.write(report)


