import os
import sys
import time
import uuid

from .tcp_flow import TcpFlow

from sqlalchemy import and_, func, or_
from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class TcpFlowDb(Base):
    '''
    Class defining the structure of the database table for tcp flows examined.

    '''

    __tablename__ = 'tcpflows'

    TcpFlowFileName = Column(String, primary_key = True)
    TcpFlowFilePath = Column(String)
    SrcIp = Column(String)
    SrcPort = Column(String)
    DestIp = Column(String)
    DestPort = Column(String)
    VLAN = Column(String)
    Timestamp = Column(String)
    ConnectionNumber = Column(String)

    def __init__(self, TcpFlowFileName, TcpFlowFilePath, SrcIp, SrcPort, DestIp,
        DestPort, Timestamp, VLAN, ConnectionNumber):
        
        self.TcpFlowFileName = TcpFlowFileName
        self.TcpFlowFilePath = TcpFlowFilePath
        self.SrcIp = SrcIp
        self.SrcPort = SrcPort
        self.DestIp = DestIp
        self.DestPort = DestPort
        self.VLAN = VLAN
        self.Timestamp = Timestamp
        self.ConnectionNumber = ConnectionNumber

class FoundFeatureDb(Base):
    '''
    Class defining the structure of the database table for tcp flows examined.

    '''
    
    __tablename__ = "features"

    id = Column(Integer, primary_key = True)
    TcpFlowFileName = Column(String, ForeignKey('tcpflows.TcpFlowFileName'))
    FeatureType = Column(String)
    Feature = Column(String)
    Position = Column(String)

    def __init__(self, TcpFlowFileName, FeatureType, Feature, Position):
        self.TcpFlowFileName = TcpFlowFileName
        self.FeatureType = FeatureType
        self.Feature = Feature
        self.Position = Position

class DatabaseController:
    '''
    Database handler for creationand manipulation of the tff output database.

    '''

    def __init__(self, db_path):
        if os.path.exists(db_path):
            db = db_path[:-3] + "_{}.db".format(uuid.uuid4().hex)
        else:
            db = db_path

        engine = create_engine('sqlite:///' + db, echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_db_session(self):
        '''
        Get a copy of the database session object.

        Returns:
            db.session

        '''

        return self.session

    def add_tcp_flow_to_session(self, tcp_flow):
        '''
        Add a row for a given TcpFlow object and push it to the db session.

        Must call db_controller.session.commit() or use commit_session() in order
        to update the row into the database.

        '''

        tcp_row = TcpFlowDb(tcp_flow.filename, tcp_flow.path, tcp_flow.source_ip,
                        tcp_flow.source_port, tcp_flow.dest_ip, tcp_flow.dest_port,
                        tcp_flow.vlan, tcp_flow.timestamp, tcp_flow.connection_number)
        self.session.add(tcp_row)

    def add_feature_to_session(self, tcpflow_filename, feature_type, feature, location):
        '''
        Add a row for a found feature to the database.

        Must call db_controller.session.commit() or use commit_session() in order
        to update the row into the database.

        '''

        feature_row = FoundFeatureDb(tcpflow_filename, feature_type, feature, location)
        self.session.add(feature_row)

    def select_features_by_type(self, feature_type):
        '''
        Return all features of a given type

        Returns:
            [('feature',)] list of given type

        '''

        return self.session.query(FoundFeatureDb)\
                            .filter(FoundFeatureDb.FeatureType == feature_type)\
                            .all()

    def count_feature_type(self):
        '''
        Returns an ordered list features and their count

        Returns:
            a list of tuples of the form [(count, 'Feature Type'), ...]

        '''

        output = self.session.query(
            func.count(FoundFeatureDb.FeatureType), FoundFeatureDb.FeatureType)\
                            .group_by(FoundFeatureDb.FeatureType).all()
        output.sort(key = lambda x:x[0])
        return output

    def count_num_features_by_ip(self):
        '''
        Returns number of features found for each IP incoming and outgoing.

        Will return a pair of lists, each of the form: [(count, IP),...] where the
        first list in the pair is source IPs and the second list in the pair is
        destination IPs.

        Returns:
            pair of lists, each of the form: [(count, IP),...] where the
                first list in the pair is source IPs and the second list in the pair is
                destination IPs.

        '''

        src_output = self.session.query(func.count(FoundFeatureDb.Feature), TcpFlowDb.SrcIp)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .group_by(TcpFlowDb.SrcIp)\
                    .all()

        dest_output = self.session.query(func.count(FoundFeatureDb.Feature), TcpFlowDb.DestIp)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .group_by(TcpFlowDb.SrcIp)\
                    .all()

        return (src_output, dest_output)

    def get_features_by_ip(self, ip):
        '''
        Get source and destination features associated with an IP address.

        Returns:
            A tuple of lists of the form ([src_features], [dest_features])

        '''

        src = self.session.query(FoundFeatureDb.Feature)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .filter(TcpFlowDb.SrcIp == ip)\
                    .all()

        dest = self.session.query(FoundFeatureDb.Feature)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .filter(TcpFlowDb.DestIp == ip)\
                    .all()

        src_features = []
        dest_features = []

        for (feature,) in src:
            src_features.append(feature)

        for (feature,) in dest:
            dest_features.append(feature)

        return (src_features, dest_features)

    def get_feature_types_by_ip(self, ip):
        '''
        Get source and destination features associated with an IP address.

        Returns:
            A tuple of lists of the form ([src_features], [dest_features])

        '''

        src = self.session.query(FoundFeatureDb.FeatureType)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .filter(TcpFlowDb.SrcIp == ip)\
                    .distinct().all()

        dest = self.session.query(FoundFeatureDb.FeatureType)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .filter(TcpFlowDb.DestIp == ip)\
                    .distinct().all()

        src_ft = []
        dest_ft = []

        for (feature,) in src:
            src_ft.append(feature)

        for (feature,) in dest:
            dest_ft.append(feature)

        return (src_ft, dest_ft)

    def get_all_ips(self):
        '''
        Returns a list of distinct IP addresses involved in flows where features were found.

        Returns:
            [ip, ....] A list of ip address strings

        '''

        src_ips = self.session.query(TcpFlowDb.SrcIp)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .distinct().all()

        dest_ips = self.session.query(TcpFlowDb.DestIp)\
                    .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                    .distinct().all()

        ips = []

        for (ip,) in src_ips:
            ips.append(ip)

        for (ip,) in dest_ips:
            if ip not in ips:
                ips.append(ip)

        return ips

    def get_paired_ips(self, ip):
        '''
        Returns a list of all IPs that interacted with the given IP.

        Returns:
            {associated ip:count of features found}

        '''

        src_ips = self.session.query(TcpFlowDb.SrcIp, FoundFeatureDb.Feature)\
                .filter(TcpFlowDb.DestIp == ip)\
                .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                .all()

        dest_ips = self.session.query(TcpFlowDb.DestIp, FoundFeatureDb.Feature)\
                .filter(TcpFlowDb.SrcIp == ip)\
                .filter(FoundFeatureDb.TcpFlowFileName == TcpFlowDb.TcpFlowFileName)\
                .all()

        ip_dict = {}

        for (ip, feature) in src_ips + dest_ips:
            if ip not in ip_dict:
                ip_dict[ip] = 1
            else:
                ip_dict[ip] += 1

        return ip_dict

    def get_feature_types_by_flow(self, flow_fn):
        '''
        Returns distinct feature types associated with a tcp flow.

        Arguments:
            flow_fn - file path of tcp flow
        Returns:
            list of associated feature types in form [('feature type',)]

        '''

        types = self.session.query(FoundFeatureDb.FeatureType)\
                    .filter(FoundFeatureDb.TcpFlowFileName == flow_fn)\
                    .distinct().all()

        return types

    def get_feature_count_by_flow(self, flow_fn):
        '''
        Return number of features found for a given tcp flow.

        Arguments:
            flow_fn - file path of tcp flow
        Returns:
            int count of features associated

        '''

        count = self.session.query(func.count(FoundFeatureDb.Feature))\
                    .filter(FoundFeatureDb.TcpFlowFileName == flow_fn)\
                    .all()

        return count[0][0]

    def get_features_by_flow(self, flow_fn):
        '''
        Return features associated with a tcp flow

        Returns:
            list of features associated with the tcp flow of form [('feature',),...]

        '''

        features = self.session.query(FoundFeatureDb.Feature)\
                    .filter(FoundFeatureDb.TcpFlowFileName == flow_fn)\
                    .all()

        return features

    def commit_session(self):
        self.session.commit()           
    


